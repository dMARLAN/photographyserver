from pathlib import Path

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from pgs_db.database import db_manager
from pgs_db.sync import sync_filesystem_to_db


class SyncRepository:
    def __init__(self, session: AsyncSession = Depends(db_manager.get_session)) -> None:
        self.__session = session

    @staticmethod
    async def sync_filesystem_to_database(storage_path: Path):  # noqa
        # TODO: Fix return type
        """Sync filesystem photos to the database."""
        return await sync_filesystem_to_db(storage_path)
