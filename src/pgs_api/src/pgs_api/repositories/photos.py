from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from pgs_db.models import Photo


class PhotosRepository:
    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    async def get_photo_by_id(self, photo_id: str):
        """Get a photo by ID."""
        result = await self._db.execute(select(Photo).where(Photo.id == photo_id))
        return result.scalar_one_or_none()
