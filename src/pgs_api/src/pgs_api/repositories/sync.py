from pathlib import Path

from pgs_db.sync import sync_filesystem_to_db


class SyncRepository:
    @staticmethod
    async def sync_filesystem_to_database(storage_path: Path):
        """Sync filesystem photos to database."""
        return await sync_filesystem_to_db(storage_path)
