from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from pgs_api.repositories.sync import SyncRepository
from pgs_api.services.sync import SyncService


class TestSyncService:
    @pytest.mark.asyncio
    async def test_sync_photos_success(self) -> None:
        # Arrange
        mock_stats = Mock()
        mock_stats.files_scanned = 100
        mock_stats.files_added = 10
        mock_stats.files_updated = 5
        mock_stats.files_removed = 2
        mock_stats.errors = []

        with patch.object(SyncRepository, "sync_filesystem_to_database") as mock_sync_repo:
            mock_sync_repo.return_value = mock_stats

            with patch("pgs_api.services.sync.api_config") as mock_config:
                mock_config.storage_path = Path("/photos")

                # Act
                result = await SyncService.sync_photos()

                # Assert
                assert result["message"] == "Sync completed successfully"
                assert result["stats"]["files_scanned"] == 100
                assert result["stats"]["files_added"] == 10
                assert result["stats"]["files_updated"] == 5
                assert result["stats"]["files_removed"] == 2
                assert result["stats"]["errors"] == []

                mock_sync_repo.assert_called_once_with(Path("/photos"))

    @pytest.mark.asyncio
    async def test_sync_photos_with_errors(self) -> None:
        # Arrange
        mock_stats = Mock()
        mock_stats.files_scanned = 50
        mock_stats.files_added = 5
        mock_stats.files_updated = 2
        mock_stats.files_removed = 1
        mock_stats.errors = ["Error processing file1.jpg", "Error processing file2.png"]

        with patch.object(SyncRepository, "sync_filesystem_to_database") as mock_sync_repo:
            mock_sync_repo.return_value = mock_stats

            with patch("pgs_api.services.sync.api_config") as mock_config:
                mock_config.storage_path = Path("/test/photos")

                # Act
                result = await SyncService.sync_photos()

                # Assert
                assert result["message"] == "Sync completed successfully"
                assert result["stats"]["files_scanned"] == 50
                assert result["stats"]["files_added"] == 5
                assert result["stats"]["files_updated"] == 2
                assert result["stats"]["files_removed"] == 1
                assert result["stats"]["errors"] == ["Error processing file1.jpg", "Error processing file2.png"]

                mock_sync_repo.assert_called_once_with(Path("/test/photos"))

    @pytest.mark.asyncio
    async def test_sync_photos_zero_changes(self) -> None:
        # Arrange
        mock_stats = Mock()
        mock_stats.files_scanned = 25
        mock_stats.files_added = 0
        mock_stats.files_updated = 0
        mock_stats.files_removed = 0
        mock_stats.errors = []

        with patch.object(SyncRepository, "sync_filesystem_to_database") as mock_sync_repo:
            mock_sync_repo.return_value = mock_stats

            with patch("pgs_api.services.sync.api_config") as mock_config:
                mock_config.storage_path = Path("/empty/photos")

                # Act
                result = await SyncService.sync_photos()

                # Assert
                assert result["message"] == "Sync completed successfully"
                assert result["stats"]["files_scanned"] == 25
                assert result["stats"]["files_added"] == 0
                assert result["stats"]["files_updated"] == 0
                assert result["stats"]["files_removed"] == 0
                assert result["stats"]["errors"] == []

                mock_sync_repo.assert_called_once_with(Path("/empty/photos"))

    @pytest.mark.asyncio
    async def test_sync_photos_repository_exception_propagates(self) -> None:
        # Arrange
        with patch.object(SyncRepository, "sync_filesystem_to_database") as mock_sync_repo:
            mock_sync_repo.side_effect = Exception("Database connection failed")

            with patch("pgs_api.services.sync.api_config") as mock_config:
                mock_config.storage_path = Path("/photos")

                # Act & Assert
                with pytest.raises(Exception, match="Database connection failed"):
                    await SyncService.sync_photos()

                mock_sync_repo.assert_called_once_with(Path("/photos"))

    @pytest.mark.asyncio
    async def test_sync_photos_static_method_behavior(self) -> None:
        # Test that sync_photos is properly implemented as a static method
        # and doesn't require an instance

        # Arrange
        mock_stats = Mock()
        mock_stats.files_scanned = 42
        mock_stats.files_added = 1
        mock_stats.files_updated = 0
        mock_stats.files_removed = 0
        mock_stats.errors = []

        with patch.object(SyncRepository, "sync_filesystem_to_database") as mock_sync_repo:
            mock_sync_repo.return_value = mock_stats

            with patch("pgs_api.services.sync.api_config") as mock_config:
                mock_config.storage_path = Path("/test")

                # Act - call directly on class without instantiation
                result = await SyncService.sync_photos()

                # Assert
                assert result["message"] == "Sync completed successfully"
                assert result["stats"]["files_scanned"] == 42
                mock_sync_repo.assert_called_once_with(Path("/test"))

    @pytest.mark.asyncio
    async def test_sync_photos_config_storage_path_used(self) -> None:
        # Test that the config's storage_path is correctly passed to the repository

        # Arrange
        custom_path = Path("/custom/storage/location")
        mock_stats = Mock()
        mock_stats.files_scanned = 1
        mock_stats.files_added = 0
        mock_stats.files_updated = 0
        mock_stats.files_removed = 0
        mock_stats.errors = []

        with patch.object(SyncRepository, "sync_filesystem_to_database") as mock_sync_repo:
            mock_sync_repo.return_value = mock_stats

            with patch("pgs_api.services.sync.api_config") as mock_config:
                mock_config.storage_path = custom_path

                # Act
                await SyncService.sync_photos()

                # Assert
                mock_sync_repo.assert_called_once_with(custom_path)
