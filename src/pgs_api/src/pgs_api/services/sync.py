import logging

from pgs_api.config import api_config
from pgs_api.repositories.sync import SyncRepository

logger = logging.getLogger(__name__)


class SyncService:
    @staticmethod
    async def sync_photos():
        """Scan filesystem and update database with photo metadata."""
        stats = await SyncRepository.sync_filesystem_to_database(api_config.storage_path)
        return {
            "message": "Sync completed successfully",
            "stats": {
                "files_scanned": stats.files_scanned,
                "files_added": stats.files_added,
                "files_updated": stats.files_updated,
                "files_removed": stats.files_removed,
                "errors": stats.errors,
            },
        }
