from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from pgs_db.models import Photo


class CategoriesService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def list_categories(self):
        """Get all available photo categories with counts and latest photo timestamp."""
        result = await self.db.execute(
            select(
                Photo.category,
                func.count(Photo.id).label("photo_count"),
                func.max(Photo.created_at).label("latest_photo"),
            )
            .group_by(Photo.category)
            .order_by(Photo.category)
        )
        categories = result.all()

        return [
            {"name": category, "photo_count": photo_count, "latest_photo": latest_photo}
            for category, photo_count, latest_photo in categories
        ]

    async def get_photos_in_category(self, category: str):
        """Get all photos in a specific category."""
        result = await self.db.execute(
            select(Photo).where(Photo.category == category).order_by(Photo.created_at.desc())
        )
        photos = result.scalars().all()

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
