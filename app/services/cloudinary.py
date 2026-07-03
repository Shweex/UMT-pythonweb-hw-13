"""Cloudinary integration for avatar uploads."""

import cloudinary
import cloudinary.uploader

from app.config import get_settings

settings = get_settings()

cloudinary.config(
    cloud_name=settings.cloudinary_name,
    api_key=settings.cloudinary_api_key,
    api_secret=settings.cloudinary_api_secret,
    secure=True,
)


def upload_avatar(file_bytes: bytes, public_id: str) -> str:
    """Upload avatar bytes to Cloudinary and return the secure URL."""
    result = cloudinary.uploader.upload(
        file_bytes,
        public_id=public_id,
        folder="avatars",
        overwrite=True,
        resource_type="image",
    )
    return result["secure_url"]
