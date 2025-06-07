from sqlalchemy.ext.asyncio import AsyncSession

from pgs_api.repositories.categories import CategoriesRepository


class CategoriesService:
    def __init__(self, db: AsyncSession) -> None:
        self._repository = CategoriesRepository(db)

    async def list_categories(self):
        """Get all available photo categories with counts and latest photo timestamp."""
        categories = await self._repository.get_categories_with_stats()
        return [
            {"name": category, "photo_count": photo_count, "latest_photo": latest_photo}
            for category, photo_count, latest_photo in categories
        ]

    async def get_photos_in_category(self, category: str):
        """Get all photos in a specific category."""
        photos = await self._repository.get_photos_by_category(category)

        if not photos:
            return None

        return [
            {
                "id": photo.id,
                "filename": photo.filename,
                "title": photo.get_display_title(),
                "width": photo.width,
                "height": photo.height,
                "aspect_ratio": photo.aspect_ratio,
                "orientation": photo.orientation,
                "file_size_mb": round(photo.file_size_mb, 2),
                "url": f"/api/v1/photos/{photo.id}/file",
                "created_at": photo.created_at,
                "file_modified_at": photo.file_modified_at,
            }
            for photo in photos
        ]
