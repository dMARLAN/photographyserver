from unittest.mock import AsyncMock, Mock

import pytest
from fastapi import HTTPException

from pgs_api.routes.sync import sync_photos
from pgs_api.services.sync import SyncService
from pgs_api.types.sync import SyncStats


class TestSyncPhotos:
    @pytest.mark.asyncio
    async def test_sync_photos_success(self) -> None:
        expected_stats = SyncStats(
            files_scanned=100,
            files_added=10,
            files_updated=5,
            files_removed=2,
            errors=0,
        )

        mock_service = Mock(spec=SyncService)
        mock_service.sync_photos = AsyncMock(return_value=expected_stats)

        result = await sync_photos(sync_service=mock_service)

        assert result == expected_stats
        mock_service.sync_photos.assert_called_once()

    @pytest.mark.asyncio
    async def test_sync_photos_file_not_found_error(self) -> None:
        mock_service = Mock(spec=SyncService)
        mock_service.sync_photos = AsyncMock(side_effect=FileNotFoundError("Storage path not found"))

        with pytest.raises(HTTPException) as exc_info:
            await sync_photos(sync_service=mock_service)

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Storage path not found"
        mock_service.sync_photos.assert_called_once()

    @pytest.mark.asyncio
    async def test_sync_photos_generic_error(self) -> None:
        mock_service = Mock(spec=SyncService)
        mock_service.sync_photos = AsyncMock(side_effect=Exception("Database connection failed"))

        with pytest.raises(HTTPException) as exc_info:
            await sync_photos(sync_service=mock_service)

        assert exc_info.value.status_code == 500
        assert exc_info.value.detail == "Sync operation failed"
        mock_service.sync_photos.assert_called_once()

    @pytest.mark.asyncio
    async def test_sync_photos_success_with_errors(self) -> None:
        expected_stats = SyncStats(
            files_scanned=50,
            files_added=5,
            files_updated=2,
            files_removed=1,
            errors=3,
        )

        mock_service = Mock(spec=SyncService)
        mock_service.sync_photos = AsyncMock(return_value=expected_stats)

        result = await sync_photos(sync_service=mock_service)

        assert result == expected_stats
        assert result.files_scanned == 50
        assert result.files_added == 5
        assert result.files_updated == 2
        assert result.files_removed == 1
        assert result.errors == 3
        mock_service.sync_photos.assert_called_once()
