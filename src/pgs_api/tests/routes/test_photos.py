from pathlib import Path
from unittest.mock import AsyncMock

import pytest
from fastapi import HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from pgs_api.routes import photos as photos_module
from pgs_api.routes.photos import get_photo_metadata, serve_photo_file
from pgs_api.services.photos import PhotosService


@pytest.fixture
def mock_db(mocker):
    return mocker.Mock(spec=AsyncSession)


@pytest.fixture
def mock_photos_service(mocker):
    return mocker.Mock(spec=PhotosService)


class TestGetPhotoMetadata:
    @pytest.mark.asyncio
    async def test_get_photo_metadata_success(self, mock_db, mock_photos_service, mocker) -> None:
        # Arrange
        photo_id = "photo123"
        expected_photo = {
            "id": photo_id,
            "filename": "test.jpg",
            "title": "Test Photo",
            "category": "nature",
            "file_path": "/photos/nature/test.jpg",
            "width": 1920,
            "height": 1080,
            "aspect_ratio": 1.78,
            "orientation": "landscape",
            "megapixels": 2.07,
            "file_size": 2621440,
            "file_size_mb": 2.5,
            "file_extension": ".jpg",
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00",
            "file_modified_at": "2024-01-01T00:00:00",
        }
        mock_photos_service.get_photo_by_id = AsyncMock(return_value=expected_photo)
        mocker.patch.object(photos_module, "PhotosService", return_value=mock_photos_service)

        # Act
        result = await get_photo_metadata(photo_id, mock_db)

        # Assert
        assert result == expected_photo
        mock_photos_service.get_photo_by_id.assert_called_once_with(photo_id)

    @pytest.mark.asyncio
    async def test_get_photo_metadata_not_found(self, mock_db, mock_photos_service, mocker) -> None:
        # Arrange
        photo_id = "nonexistent"
        mock_photos_service.get_photo_by_id = AsyncMock(return_value=None)
        mocker.patch.object(photos_module, "PhotosService", return_value=mock_photos_service)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await get_photo_metadata(photo_id, mock_db)

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Photo not found"
        mock_photos_service.get_photo_by_id.assert_called_once_with(photo_id)


class TestServePhotoFile:
    @pytest.mark.asyncio
    async def test_serve_photo_file_success(self, mock_db, mock_photos_service, mocker) -> None:
        # Arrange
        photo_id = "photo123"
        test_path = Path("/tmp/test.jpg")
        file_info = {"file_path": test_path, "media_type": "image/jpeg", "filename": "test.jpg"}
        mock_photos_service.get_photo_file_info = AsyncMock(return_value=file_info)
        mocker.patch.object(photos_module, "PhotosService", return_value=mock_photos_service)
        mocker.patch.object(Path, "exists", return_value=True)

        # Act
        result = await serve_photo_file(photo_id, mock_db)

        # Assert
        assert isinstance(result, FileResponse)
        mock_photos_service.get_photo_file_info.assert_called_once_with(photo_id)

    @pytest.mark.asyncio
    async def test_serve_photo_file_photo_not_found(self, mock_db, mock_photos_service, mocker) -> None:
        # Arrange
        photo_id = "nonexistent"
        mock_photos_service.get_photo_file_info = AsyncMock(return_value=None)
        mocker.patch.object(photos_module, "PhotosService", return_value=mock_photos_service)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await serve_photo_file(photo_id, mock_db)

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Photo not found"
        mock_photos_service.get_photo_file_info.assert_called_once_with(photo_id)

    @pytest.mark.asyncio
    async def test_serve_photo_file_file_not_on_disk(self, mock_db, mock_photos_service, mocker) -> None:
        # Arrange
        photo_id = "photo123"
        test_path = Path("/tmp/nonexistent.jpg")
        file_info = {"file_path": test_path, "media_type": "image/jpeg", "filename": "test.jpg"}
        mock_photos_service.get_photo_file_info = AsyncMock(return_value=file_info)
        mocker.patch.object(photos_module, "PhotosService", return_value=mock_photos_service)
        mocker.patch.object(Path, "exists", return_value=False)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await serve_photo_file(photo_id, mock_db)

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Photo file not found on disk"
        mock_photos_service.get_photo_file_info.assert_called_once_with(photo_id)
