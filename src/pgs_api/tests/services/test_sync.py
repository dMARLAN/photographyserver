from pathlib import Path
from unittest.mock import Mock, AsyncMock

import pytest

from pgs_api.config import APIConfig
from pgs_api.repositories.sync import SyncRepository
from pgs_api.services.sync import SyncService


class TestSyncService:
    @pytest.mark.asyncio
    async def test_sync_photos_success(self) -> None:
        mock_stats = Mock()
        mock_stats.files_scanned = 100
        mock_stats.files_added = 10
        mock_stats.files_updated = 5
        mock_stats.files_removed = 2
        mock_stats.errors = 0

        mock_repository = Mock(spec=SyncRepository)
        mock_repository.sync_filesystem_to_database = AsyncMock(return_value=mock_stats)

        mock_config = Mock(spec=APIConfig)
        mock_config.storage_path = Path("/photos")

        service = SyncService(sync_repository=mock_repository, api_config=mock_config)
        result = await service.sync_photos()

        assert result.files_scanned == 100
        assert result.files_added == 10
        assert result.files_updated == 5
        assert result.files_removed == 2
        assert result.errors == 0

        mock_repository.sync_filesystem_to_database.assert_called_once_with(Path("/photos"))

    @pytest.mark.asyncio
    async def test_sync_photos_with_errors(self) -> None:
        mock_stats = Mock()
        mock_stats.files_scanned = 50
        mock_stats.files_added = 5
        mock_stats.files_updated = 2
        mock_stats.files_removed = 1
        mock_stats.errors = 2

        mock_repository = Mock(spec=SyncRepository)
        mock_repository.sync_filesystem_to_database = AsyncMock(return_value=mock_stats)

        mock_config = Mock(spec=APIConfig)
        mock_config.storage_path = Path("/test/photos")

        service = SyncService(sync_repository=mock_repository, api_config=mock_config)
        result = await service.sync_photos()

        assert result.files_scanned == 50
        assert result.files_added == 5
        assert result.files_updated == 2
        assert result.files_removed == 1
        assert result.errors == 2

        mock_repository.sync_filesystem_to_database.assert_called_once_with(Path("/test/photos"))

    @pytest.mark.asyncio
    async def test_sync_photos_zero_changes(self) -> None:
        mock_stats = Mock()
        mock_stats.files_scanned = 25
        mock_stats.files_added = 0
        mock_stats.files_updated = 0
        mock_stats.files_removed = 0
        mock_stats.errors = 0

        mock_repository = Mock(spec=SyncRepository)
        mock_repository.sync_filesystem_to_database = AsyncMock(return_value=mock_stats)

        mock_config = Mock(spec=APIConfig)
        mock_config.storage_path = Path("/empty/photos")

        service = SyncService(sync_repository=mock_repository, api_config=mock_config)
        result = await service.sync_photos()

        assert result.files_scanned == 25
        assert result.files_added == 0
        assert result.files_updated == 0
        assert result.files_removed == 0
        assert result.errors == 0

        mock_repository.sync_filesystem_to_database.assert_called_once_with(Path("/empty/photos"))

    @pytest.mark.asyncio
    async def test_sync_photos_repository_exception_propagates(self) -> None:
        mock_repository = Mock(spec=SyncRepository)
        mock_repository.sync_filesystem_to_database = AsyncMock(side_effect=Exception("Database connection failed"))

        mock_config = Mock(spec=APIConfig)
        mock_config.storage_path = Path("/photos")

        service = SyncService(sync_repository=mock_repository, api_config=mock_config)

        with pytest.raises(Exception, match="Database connection failed"):
            await service.sync_photos()

        mock_repository.sync_filesystem_to_database.assert_called_once_with(Path("/photos"))

    @pytest.mark.asyncio
    async def test_sync_photos_static_method_behavior(self) -> None:
        mock_stats = Mock()
        mock_stats.files_scanned = 42
        mock_stats.files_added = 1
        mock_stats.files_updated = 0
        mock_stats.files_removed = 0
        mock_stats.errors = 0

        mock_repository = Mock(spec=SyncRepository)
        mock_repository.sync_filesystem_to_database = AsyncMock(return_value=mock_stats)

        mock_config = Mock(spec=APIConfig)
        mock_config.storage_path = Path("/test")

        service = SyncService(sync_repository=mock_repository, api_config=mock_config)
        result = await service.sync_photos()

        assert result.files_scanned == 42
        mock_repository.sync_filesystem_to_database.assert_called_once_with(Path("/test"))

    @pytest.mark.asyncio
    async def test_sync_photos_config_storage_path_used(self) -> None:
        custom_path = Path("/custom/storage/location")
        mock_stats = Mock()
        mock_stats.files_scanned = 1
        mock_stats.files_added = 0
        mock_stats.files_updated = 0
        mock_stats.files_removed = 0
        mock_stats.errors = 0

        mock_repository = Mock(spec=SyncRepository)
        mock_repository.sync_filesystem_to_database = AsyncMock(return_value=mock_stats)

        mock_config = Mock(spec=APIConfig)
        mock_config.storage_path = custom_path

        service = SyncService(sync_repository=mock_repository, api_config=mock_config)
        await service.sync_photos()

        mock_repository.sync_filesystem_to_database.assert_called_once_with(custom_path)
