from unittest.mock import AsyncMock, patch

import pytest
from fastapi import HTTPException

from pgs_api.routes.sync import sync_photos
from pgs_api.services.sync import SyncService


class MockSyncStats:
    def __init__(self, files_scanned=0, files_added=0, files_updated=0, files_removed=0, errors=0):
        self.files_scanned = files_scanned
        self.files_added = files_added
        self.files_updated = files_updated
        self.files_removed = files_removed
        self.errors = errors


class TestSyncPhotos:
    @pytest.mark.asyncio
    async def test_sync_photos_success(self):
        expected_result = {
            "message": "Sync completed successfully",
            "stats": {
                "files_scanned": 100,
                "files_added": 10,
                "files_updated": 5,
                "files_removed": 2,
                "errors": 0,
            },
        }

        with patch.object(SyncService, "sync_photos", new_callable=AsyncMock) as mock_sync:
            mock_sync.return_value = expected_result

            result = await sync_photos()

        assert result == expected_result
        mock_sync.assert_called_once()

    @pytest.mark.asyncio
    async def test_sync_photos_file_not_found_error(self):
        with patch.object(SyncService, "sync_photos", new_callable=AsyncMock) as mock_sync:
            mock_sync.side_effect = FileNotFoundError("Storage path not found")

            with pytest.raises(HTTPException) as exc_info:
                await sync_photos()

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Storage path not found"
        mock_sync.assert_called_once()

    @pytest.mark.asyncio
    async def test_sync_photos_generic_error(self):
        with patch.object(SyncService, "sync_photos", new_callable=AsyncMock) as mock_sync:
            mock_sync.side_effect = Exception("Database connection failed")

            with pytest.raises(HTTPException) as exc_info:
                await sync_photos()

        assert exc_info.value.status_code == 500
        assert exc_info.value.detail == "Sync operation failed"
        mock_sync.assert_called_once()

    @pytest.mark.asyncio
    async def test_sync_photos_success_with_errors(self):
        expected_result = {
            "message": "Sync completed successfully",
            "stats": {
                "files_scanned": 50,
                "files_added": 5,
                "files_updated": 0,
                "files_removed": 0,
                "errors": 3,
            },
        }

        with patch.object(SyncService, "sync_photos", new_callable=AsyncMock) as mock_sync:
            mock_sync.return_value = expected_result

            result = await sync_photos()

        assert result == expected_result
        assert result["stats"]["errors"] == 3
        mock_sync.assert_called_once()
