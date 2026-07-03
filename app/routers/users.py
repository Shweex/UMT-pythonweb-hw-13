"""User profile routes."""

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import _serialize_user, get_current_user, require_admin
from app.limiter import limiter
from app.models import User
from app.repositories import UserRepository
from app.schemas.user import UserResponse
from app.services.cache import UserCache, get_user_cache
from app.services.cloudinary import upload_avatar

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
@limiter.limit("5/minute")
def get_current_user_profile(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    """Return the authenticated user's profile."""
    return current_user


@router.patch("/me/avatar", response_model=UserResponse)
async def update_avatar(
    file: UploadFile = File(...),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
    cache: UserCache = Depends(get_user_cache),
):
    """Upload a new avatar. Only administrators may change their default avatar."""
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File must be an image")

    file_bytes = await file.read()
    avatar_url = upload_avatar(file_bytes, public_id=str(current_user.id))
    user_repo = UserRepository(db)
    db_user = user_repo.get_by_id(current_user.id)
    if db_user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    updated_user = user_repo.update_avatar(db_user, avatar_url)
    cache.set_user(updated_user.id, _serialize_user(updated_user))
    return updated_user
