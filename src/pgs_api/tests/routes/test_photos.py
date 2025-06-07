from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi import HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession

from pgs_api.routes import photos as photos_module
from pgs_api.routes.photos import get_photo_metadata, serve_photo_file_info
from pgs_api.services.photos import PhotosService


@pytest.fixture
def mock_db() -> Mock:
    return Mock(spec=AsyncSession)


@pytest.fixture
def mock_photos_service() -> Mock:
    return Mock(spec=PhotosService)


class TestGetPhotoMetadata:
    @pytest.mark.asyncio
    async def test_get_photo_metadata_success(self, mock_db: Mock, mock_photos_service: Mock) -> None:
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

        with patch.object(photos_module, "PhotosService", return_value=mock_photos_service):
            result = await get_photo_metadata(photo_id, mock_db)

            assert result == expected_photo
            mock_photos_service.get_photo_by_id.assert_called_once_with(photo_id)

    @pytest.mark.asyncio
    async def test_get_photo_metadata_not_found(self, mock_db: Mock, mock_photos_service: Mock) -> None:
        photo_id = "nonexistent"
        mock_photos_service.get_photo_by_id = AsyncMock(return_value=None)

        with patch.object(photos_module, "PhotosService", return_value=mock_photos_service):
            with pytest.raises(HTTPException) as exc_info:
                await get_photo_metadata(photo_id, mock_db)

            assert exc_info.value.status_code == 404
            assert exc_info.value.detail == "Photo not found"
            mock_photos_service.get_photo_by_id.assert_called_once_with(photo_id)


class TestServePhotoFile:
    @pytest.mark.asyncio
    async def test_serve_photo_file_success(self, mock_db: Mock, mock_photos_service: Mock) -> None:
        photo_id = "photo123"
        test_path = Path("/tmp/test.jpg")
        file_info = {"file_path": test_path, "media_type": "image/jpeg", "filename": "test.jpg"}
        mock_photos_service.get_photo_file_info = AsyncMock(return_value=file_info)

        with (
            patch.object(photos_module, "PhotosService", return_value=mock_photos_service),
            patch.object(Path, "exists", return_value=True),
        ):
            result = await serve_photo_file_info(photo_id, mock_db)

            assert isinstance(result, FileResponse)
            mock_photos_service.get_photo_file_info.assert_called_once_with(photo_id)

    @pytest.mark.asyncio
    async def test_serve_photo_file_photo_not_found(self, mock_db: Mock, mock_photos_service: Mock) -> None:
        photo_id = "nonexistent"
        mock_photos_service.get_photo_file_info = AsyncMock(return_value=None)

        with patch.object(photos_module, "PhotosService", return_value=mock_photos_service):
            with pytest.raises(HTTPException) as exc_info:
                await serve_photo_file_info(photo_id, mock_db)

            assert exc_info.value.status_code == 404
            assert exc_info.value.detail == "Photo not found"
            mock_photos_service.get_photo_file_info.assert_called_once_with(photo_id)

    @pytest.mark.asyncio
    async def test_serve_photo_file_file_not_on_disk(self, mock_db: Mock, mock_photos_service: Mock) -> None:
        photo_id = "photo123"
        test_path = Path("/tmp/nonexistent.jpg")
        file_info = {"file_path": test_path, "media_type": "image/jpeg", "filename": "test.jpg"}
        mock_photos_service.get_photo_file_info = AsyncMock(return_value=file_info)

        with (
            patch.object(photos_module, "PhotosService", return_value=mock_photos_service),
            patch.object(Path, "exists", return_value=False),
        ):
            with pytest.raises(HTTPException) as exc_info:
                await serve_photo_file_info(photo_id, mock_db)

            assert exc_info.value.status_code == 404
            assert exc_info.value.detail == "Photo file not found on disk"
            mock_photos_service.get_photo_file_info.assert_called_once_with(photo_id)
