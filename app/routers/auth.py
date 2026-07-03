"""Authentication routes: registration, login, verification, and password reset."""

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.dependencies import _serialize_user
from app.models import User, UserRole
from app.repositories import UserRepository
from app.schemas.user import (
    EmailVerificationResponse,
    MessageResponse,
    PasswordResetConfirm,
    PasswordResetRequest,
    TokenResponse,
    UserCreate,
    UserLogin,
    UserResponse,
)
from app.services.auth import (
    create_access_token,
    create_email_verification_token,
    create_password_reset_token,
    decode_email_verification_token,
    decode_password_reset_token,
    hash_password,
    verify_password,
)
from app.services.cache import UserCache, get_user_cache
from app.services.email import send_password_reset_email, send_verification_email

router = APIRouter(prefix="/api/auth", tags=["auth"])
settings = get_settings()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(payload: UserCreate, request: Request, db: Session = Depends(get_db)):
    """Register a new user and send an email verification link."""
    user_repo = UserRepository(db)
    if user_repo.get_by_email(payload.email):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User with this email already exists")

    user = User(
        email=payload.email,
        username=payload.username,
        hashed_password=hash_password(payload.password),
        avatar_url=settings.default_avatar_url,
        role=UserRole.USER,
    )
    user = user_repo.create(user)

    token = create_email_verification_token(user.email)
    base_url = str(request.base_url).rstrip("/")
    await send_verification_email(user.email, token, base_url)

    return user


@router.post("/login", response_model=TokenResponse)
def login_user(
    payload: UserLogin,
    db: Session = Depends(get_db),
    cache: UserCache = Depends(get_user_cache),
):
    """Authenticate a user and cache their profile in Redis."""
    user_repo = UserRepository(db)
    user = user_repo.get_by_username(payload.username)
    if user is None or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    cache.set_user(user.id, _serialize_user(user))
    access_token = create_access_token(str(user.id))
    return TokenResponse(access_token=access_token)


@router.get("/verify/{token}", response_model=EmailVerificationResponse)
def verify_email(token: str, db: Session = Depends(get_db)):
    """Verify a user's email address using a signed token."""
    email = decode_email_verification_token(token)
    if email is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token")

    user_repo = UserRepository(db)
    user = user_repo.get_by_email(email)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if not user.is_verified:
        user_repo.mark_verified(user)

    return EmailVerificationResponse(message="Email successfully verified", email=user.email)


@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(payload: PasswordResetRequest, request: Request, db: Session = Depends(get_db)):
    """Send a password reset link to the user's email if the account exists."""
    user_repo = UserRepository(db)
    user = user_repo.get_by_email(payload.email)
    if user is not None:
        token = create_password_reset_token(user.email)
        base_url = str(request.base_url).rstrip("/")
        await send_password_reset_email(user.email, token, base_url)

    return MessageResponse(message="If the email exists, a password reset link has been sent")


@router.post("/reset-password/{token}", response_model=MessageResponse)
def reset_password(
    token: str,
    payload: PasswordResetConfirm,
    db: Session = Depends(get_db),
    cache: UserCache = Depends(get_user_cache),
):
    """Reset the user's password using a valid reset token."""
    email = decode_password_reset_token(token)
    if email is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired token")

    user_repo = UserRepository(db)
    user = user_repo.get_by_email(email)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user_repo.update_password(user, hash_password(payload.new_password))
    cache.delete_user(user.id)
    return MessageResponse(message="Password has been reset successfully")
