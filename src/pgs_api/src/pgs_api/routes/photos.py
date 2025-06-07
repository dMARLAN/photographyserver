from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy import select

from pgs_db.models import Photo
from pgs_api.dependencies import DatabaseSession

router = APIRouter(prefix="/photos", tags=["photos"])


@router.get("/{photo_id}")
async def get_photo_metadata(photo_id: str, db: DatabaseSession):
    """Get metadata for a specific photo."""
    result = await db.execute(select(Photo).where(Photo.id == photo_id))
    photo = result.scalar_one_or_none()

    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")

    return {
        "id": photo.id,
        "filename": photo.filename,
        "title": photo.get_display_title(),
        "category": photo.category,
        "file_path": photo.file_path,
        "width": photo.width,
        "height": photo.height,
        "aspect_ratio": photo.aspect_ratio,
        "orientation": photo.orientation,
        "megapixels": photo.megapixels,
        "file_size": photo.file_size,
        "file_size_mb": round(photo.file_size_mb, 2),
        "file_extension": photo.file_extension,
        "created_at": photo.created_at,
        "updated_at": photo.updated_at,
        "file_modified_at": photo.file_modified_at,
    }


@router.get("/{photo_id}/file")
async def serve_photo_file(photo_id: str, db: DatabaseSession):
    """Serve the actual image file for a photo."""
    result = await db.execute(select(Photo).where(Photo.id == photo_id))
    photo = result.scalar_one_or_none()

    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")

    file_path = Path(photo.file_path)
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Photo file not found on disk")

    # Determine media type based on file extension
    media_type_map = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp",
        ".gif": "image/gif",
        ".bmp": "image/bmp",
        ".tiff": "image/tiff",
        ".tif": "image/tiff",
    }

    media_type = media_type_map.get(photo.file_extension.lower(), "application/octet-stream")

    return FileResponse(path=file_path, media_type=media_type, filename=photo.filename)
