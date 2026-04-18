"""
Image processing and storage service - Phase 5 Performance Optimization

Handles pet image uploads with automatic resizing to multiple formats:
- Thumbnail: 100x100 (WebP)
- Preview: 400x400 (WebP)
- Full: 800x800 (WebP)

Validates image format, size, and automatically compresses to WebP.
"""

import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from fastapi import HTTPException, UploadFile
from PIL import Image
import io

# Configuration
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_FORMATS = {"image/jpeg", "image/png", "image/webp"}
UPLOADS_DIR = Path("./uploads/pets")
COMPRESS_QUALITY = 85


class ImageService:
    """Service for handling pet image uploads and processing."""

    # Image sizes (width x height)
    SIZES = {
        "thumbnail": (100, 100),
        "preview": (400, 400),
        "full": (800, 800),
    }

    @staticmethod
    def create_uploads_directory():
        """Ensure uploads directory exists."""
        UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def get_pet_image_dir(pet_id: int) -> Path:
        """Get the directory path for a pet's images."""
        return UPLOADS_DIR / str(pet_id)

    @staticmethod
    def validate_image(file: UploadFile) -> None:
        """
        Validate image file.

        Raises HTTPException if invalid.
        """
        # Check MIME type
        if file.content_type not in ALLOWED_FORMATS:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid image format. Allowed: {', '.join(ALLOWED_FORMATS)}"
            )

        # Check file size (will be checked when reading)
        # Size check happens during file read to avoid reading entire file twice

    @staticmethod
    async def save_pet_image(pet_id: int, file: UploadFile) -> Dict[str, Any]:
        """
        Save and resize pet image to multiple formats.

        Args:
            pet_id: ID of the pet
            file: Uploaded file

        Returns:
            Dictionary with image_url and sizes info

        Raises:
            HTTPException: If file is invalid or processing fails
        """
        ImageService.create_uploads_directory()
        ImageService.validate_image(file)

        # Create pet directory
        pet_dir = ImageService.get_pet_image_dir(pet_id)
        pet_dir.mkdir(parents=True, exist_ok=True)

        try:
            # Read file content
            content = await file.read()

            # Check file size
            if len(content) > MAX_IMAGE_SIZE:
                raise HTTPException(
                    status_code=400,
                    detail=f"File too large. Max size: {MAX_IMAGE_SIZE / 1024 / 1024}MB"
                )

            # Open image
            img = Image.open(io.BytesIO(content))

            # Convert RGBA to RGB if needed (for JPEG compatibility)
            if img.mode in ("RGBA", "LA", "P"):
                # Create white background
                background = Image.new("RGB", img.size, (255, 255, 255))
                if img.mode == "P":
                    img = img.convert("RGBA")
                background.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
                img = background

            # Save resized images
            saved_files = {}
            for size_name, (width, height) in ImageService.SIZES.items():
                filename = f"pet-{pet_id}-{size_name}.webp"
                filepath = pet_dir / filename

                # Resize image
                resized = img.copy()
                resized.thumbnail((width, height), Image.Resampling.LANCZOS)

                # Create square canvas
                square = Image.new("RGB", (width, height), (255, 255, 255))
                offset = ((width - resized.width) // 2, (height - resized.height) // 2)
                square.paste(resized, offset)

                # Save as WebP
                square.save(filepath, "WEBP", quality=COMPRESS_QUALITY)
                saved_files[size_name] = filename

            return {
                "image_url": f"/api/v1/uploads/pets/{pet_id}/image.webp",
                "sizes": {
                    "thumbnail": f"/api/v1/uploads/pets/{pet_id}/{saved_files['thumbnail']}",
                    "preview": f"/api/v1/uploads/pets/{pet_id}/{saved_files['preview']}",
                    "full": f"/api/v1/uploads/pets/{pet_id}/{saved_files['full']}",
                },
                "uploaded_at": datetime.utcnow().isoformat(),
            }

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to process image: {str(e)}"
            )

    @staticmethod
    def delete_pet_image(pet_id: int) -> bool:
        """
        Delete all images for a pet.

        Args:
            pet_id: ID of the pet

        Returns:
            True if deleted successfully, False if directory didn't exist
        """
        pet_dir = ImageService.get_pet_image_dir(pet_id)

        if not pet_dir.exists():
            return False

        try:
            shutil.rmtree(pet_dir)
            return True
        except Exception as e:
            print(f"Failed to delete pet {pet_id} images: {e}")
            return False

    @staticmethod
    def get_image_path(pet_id: int, filename: str) -> Optional[Path]:
        """
        Get the full path to a pet's image file.

        Args:
            pet_id: ID of the pet
            filename: Name of the image file

        Returns:
            Path object if file exists, None otherwise
        """
        filepath = ImageService.get_pet_image_dir(pet_id) / filename

        # Security: prevent directory traversal attacks
        try:
            # Ensure the resolved path is within the uploads directory
            filepath.resolve().relative_to(UPLOADS_DIR.resolve())
        except ValueError:
            return None

        if filepath.exists() and filepath.is_file():
            return filepath

        return None

    @staticmethod
    def has_image(pet_id: int) -> bool:
        """Check if a pet has any images."""
        pet_dir = ImageService.get_pet_image_dir(pet_id)
        if not pet_dir.exists():
            return False
        return any(pet_dir.glob("pet-*.webp"))


# Singleton instance
image_service = ImageService()
