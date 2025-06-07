from datetime import datetime
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest
from fastapi import HTTPException
from fastapi.responses import FileResponse

from pgs_api.routes.photos import get_photo_metadata, serve_photo_file_info
from pgs_api.services.photos import PhotosService, PhotoFileInfo
from pgs_api.models import Photo


class TestGetPhotoMetadata:
    @pytest.mark.asyncio
    async def test_get_photo_metadata_success(self) -> None:
        photo_id = "photo123"
        expected_photo = Photo(
            id=photo_id,
            filename="test.jpg",
            file_path=Path("/photos/nature/test.jpg"),
            category="nature",
            title="Test Photo",
            file_size=2621440,
            width=1920,
            height=1080,
            created_at=datetime(2024, 1, 1),
            updated_at=datetime(2024, 1, 1),
            file_modified_at=datetime(2024, 1, 1),
        )

        mock_service = Mock(spec=PhotosService)
        mock_service.get_photo_by_id = AsyncMock(return_value=expected_photo)

        result = await get_photo_metadata(photo_id, photo_service=mock_service)

        assert result == expected_photo
        mock_service.get_photo_by_id.assert_called_once_with(photo_id)

    @pytest.mark.asyncio
    async def test_get_photo_metadata_not_found(self) -> None:
        photo_id = "nonexistent"

        mock_service = Mock(spec=PhotosService)
        mock_service.get_photo_by_id = AsyncMock(return_value=None)

        with pytest.raises(HTTPException) as exc_info:
            await get_photo_metadata(photo_id, photo_service=mock_service)

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Photo not found"
        mock_service.get_photo_by_id.assert_called_once_with(photo_id)


class TestServePhotoFile:
    @pytest.mark.asyncio
    async def test_serve_photo_file_success(self) -> None:
        photo_id = "photo123"
        test_path = Path("/photos/test.jpg")
        photo_file_info = PhotoFileInfo(
            file_path=test_path,
            media_type="image/jpeg",
            filename="test.jpg",
        )

        mock_service = Mock(spec=PhotosService)
        mock_service.get_photo_file_info = AsyncMock(return_value=photo_file_info)

        # Mock the file existence check
        with patch("pathlib.Path.exists", return_value=True):
            result = await serve_photo_file_info(photo_id, photo_service=mock_service)

            assert isinstance(result, FileResponse)
            mock_service.get_photo_file_info.assert_called_once_with(photo_id)

    @pytest.mark.asyncio
    async def test_serve_photo_file_photo_not_found(self) -> None:
        photo_id = "nonexistent"

        mock_service = Mock(spec=PhotosService)
        mock_service.get_photo_file_info = AsyncMock(return_value=None)

        with pytest.raises(HTTPException) as exc_info:
            await serve_photo_file_info(photo_id, photo_service=mock_service)

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Photo not found"
        mock_service.get_photo_file_info.assert_called_once_with(photo_id)

    @pytest.mark.asyncio
    async def test_serve_photo_file_file_not_on_disk(self) -> None:
        photo_id = "photo123"
        test_path = Path("/photos/nonexistent.jpg")
        photo_file_info = PhotoFileInfo(
            file_path=test_path,
            media_type="image/jpeg",
            filename="nonexistent.jpg",
        )

        mock_service = Mock(spec=PhotosService)
        mock_service.get_photo_file_info = AsyncMock(return_value=photo_file_info)

        # Mock the file existence check to return False
        with patch("pathlib.Path.exists", return_value=False):
            with pytest.raises(HTTPException) as exc_info:
                await serve_photo_file_info(photo_id, photo_service=mock_service)

            assert exc_info.value.status_code == 404
            assert exc_info.value.detail == "Photo file not found on disk"
            mock_service.get_photo_file_info.assert_called_once_with(photo_id)
