from pathlib import Path

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from pgs_api.types.sync import SyncStats
from pgs_db.database import db_manager
from pgs_db.sync import sync_filesystem_to_db


class SyncRepository:
    def __init__(self, session: AsyncSession = Depends(db_manager.get_session)) -> None:
        self.__session = session

    async def sync_filesystem_to_database(self, storage_path: Path) -> SyncStats:
        """Sync filesystem photos to the database."""
        return await sync_filesystem_to_db(session=self.__session, storage_path=storage_path)
