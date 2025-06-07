from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from starlette.status import HTTP_200_OK

from pgs_api.models import Photo
from pgs_api.services.photos import PhotosService

router = APIRouter(prefix="/photos", tags=["photos"])


@router.get("/{photo_id}", response_model=Photo, status_code=HTTP_200_OK)
async def get_photo_metadata(
    photo_id: str,
    photo_service: PhotosService = Depends(PhotosService),
) -> Photo:
    """Get metadata for a specific photo."""
    photo = await photo_service.get_photo_by_id(photo_id)

    if not photo:
        raise HTTPException(status_code=404, detail="Photo not found")

    return photo


@router.get("/{photo_id}/file", status_code=HTTP_200_OK)
async def serve_photo_file_info(
    photo_id: str,
    photo_service: PhotosService = Depends(PhotosService),
) -> FileResponse:
    """Serve the actual image file for a photo."""
    photo_file_info = await photo_service.get_photo_file_info(photo_id)

    if not photo_file_info:
        raise HTTPException(status_code=404, detail="Photo not found")

    if not photo_file_info.file_path.exists():
        raise HTTPException(status_code=404, detail="Photo file not found on disk")

    return FileResponse(
        path=photo_file_info.file_path,
        media_type=photo_file_info.media_type,
        filename=photo_file_info.filename,
    )
