import logging

from fastapi import Depends

from pgs_api.config import get_api_config, APIConfig
from pgs_api.repositories.sync import SyncRepository
from pgs_api.types.sync import SyncStats

logger = logging.getLogger(__name__)


class SyncService:
    def __init__(
        self,
        sync_repository: SyncRepository = Depends(SyncRepository),
        api_config: APIConfig = Depends(get_api_config),
    ) -> None:
        self.__repository = sync_repository
        self.__api_config = api_config

    async def sync_photos(self) -> SyncStats:
        """Scan filesystem and update database with photo metadata."""
        stats = await self.__repository.sync_filesystem_to_database(self.__api_config.storage_path)
        return SyncStats(
            files_scanned=stats.files_scanned,
            files_added=stats.files_added,
            files_updated=stats.files_updated,
            files_removed=stats.files_removed,
            errors=stats.errors,
        )
