from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from pgs_api.dependencies import DatabaseSession
from pgs_api.services.photos import PhotosService

router = APIRouter(prefix="/photos", tags=["photos"])


@router.get("/{photo_id}")
async def get_photo_metadata(photo_id: str, db: DatabaseSession):
    """Get metadata for a specific photo."""
    service = PhotosService(db)
    photo = await service.get_photo_by_id(photo_id)

    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")

    return photo


@router.get("/{photo_id}/file")
async def serve_photo_file(photo_id: str, db: DatabaseSession):
    """Serve the actual image file for a photo."""
    service = PhotosService(db)
    file_info = await service.get_photo_file_info(photo_id)

    if not file_info:
        raise HTTPException(status_code=404, detail="Photo not found")

    if not file_info["file_path"].exists():
        raise HTTPException(status_code=404, detail="Photo file not found on disk")

    return FileResponse(path=file_info["file_path"], media_type=file_info["media_type"], filename=file_info["filename"])
