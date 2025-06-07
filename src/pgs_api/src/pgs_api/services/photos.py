from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from pgs_api.repositories.photos import PhotosRepository


class PhotosService:
    def __init__(self, db: AsyncSession) -> None:
        self._repository = PhotosRepository(db)

    @staticmethod
    def __get_media_type(file_extension: str) -> str:
        """Get media type based on file extension."""
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
        return media_type_map.get(file_extension.lower(), "application/octet-stream")

    async def get_photo_by_id(self, photo_id: str):
        """Get photo metadata by ID."""
        photo = await self._repository.get_photo_by_id(photo_id)

        if not photo:
            return None

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

    async def get_photo_file_info(self, photo_id: str):
        """Get photo file information for serving the file."""
        photo = await self._repository.get_photo_by_id(photo_id)

        if not photo:
            return None

        file_path = Path(photo.file_path)
        if not file_path.exists():
            return None

        media_type = self.__get_media_type(photo.file_extension)

        return {
            "file_path": file_path,
            "media_type": media_type,
            "filename": photo.filename,
        }
