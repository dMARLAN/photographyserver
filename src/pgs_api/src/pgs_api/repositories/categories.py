from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from pgs_db.models import Photo


class CategoriesRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_categories_with_stats(self):
        """Get all categories with photo counts and latest photo timestamp."""
        result = await self._db.execute(
            select(
                Photo.category,
                func.count(Photo.id).label("photo_count"),
                func.max(Photo.created_at).label("latest_photo"),
            )
            .group_by(Photo.category)
            .order_by(Photo.category)
        )
        return result.all()

    async def get_photos_by_category(self, category: str):
        """Get all photos in a specific category."""
        result = await self._db.execute(
            select(Photo).where(Photo.category == category).order_by(Photo.created_at.desc())
        )
        return result.scalars().all()
