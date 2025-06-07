from unittest.mock import AsyncMock, Mock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from pgs_api.repositories.photos import PhotosRepository
from pgs_api.services.photos import PhotosService


@pytest.fixture
def mock_db():
    return Mock(spec=AsyncSession)


class TestPhotosService:

    @pytest.mark.asyncio
    async def test_get_photo_by_id_success(self, mock_db):
        # Arrange
        photo_id = "photo123"
        mock_photo = Mock()
        mock_photo.id = photo_id
        mock_photo.filename = "test.jpg"
        mock_photo.get_display_title.return_value = "Test Photo"
        mock_photo.category = "nature"
        mock_photo.file_path = "/photos/nature/test.jpg"
        mock_photo.width = 1920
        mock_photo.height = 1080
        mock_photo.aspect_ratio = 1.78
        mock_photo.orientation = "landscape"
        mock_photo.megapixels = 2.07
        mock_photo.file_size = 2621440
        mock_photo.file_size_mb = 2.5
        mock_photo.file_extension = ".jpg"
        mock_photo.created_at = "2024-01-01T00:00:00"
        mock_photo.updated_at = "2024-01-01T00:00:00"
        mock_photo.file_modified_at = "2024-01-01T00:00:00"

        with patch.object(PhotosRepository, "get_photo_by_id", new_callable=AsyncMock) as mock_get_photo:
            mock_get_photo.return_value = mock_photo

            service = PhotosService(mock_db)

            # Act
            result = await service.get_photo_by_id(photo_id)

            # Assert
            assert result is not None
            assert result["id"] == photo_id
            assert result["filename"] == "test.jpg"
            assert result["title"] == "Test Photo"
            assert result["category"] == "nature"
            assert result["file_path"] == "/photos/nature/test.jpg"
            assert result["width"] == 1920
            assert result["height"] == 1080
            assert result["aspect_ratio"] == 1.78
            assert result["orientation"] == "landscape"
            assert result["megapixels"] == 2.07
            assert result["file_size"] == 2621440
            assert result["file_size_mb"] == 2.5
            assert result["file_extension"] == ".jpg"
            assert result["created_at"] == "2024-01-01T00:00:00"
            assert result["updated_at"] == "2024-01-01T00:00:00"
            assert result["file_modified_at"] == "2024-01-01T00:00:00"

            mock_get_photo.assert_called_once_with(photo_id)
            mock_photo.get_display_title.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_photo_by_id_not_found(self, mock_db):
        # Arrange
        photo_id = "nonexistent"

        with patch.object(PhotosRepository, "get_photo_by_id", new_callable=AsyncMock) as mock_get_photo:
            mock_get_photo.return_value = None

            service = PhotosService(mock_db)

            # Act
            result = await service.get_photo_by_id(photo_id)

            # Assert
            assert result is None
            mock_get_photo.assert_called_once_with(photo_id)

    @pytest.mark.asyncio
    async def test_get_photo_file_info_success(self, mock_db):
        # Arrange
        photo_id = "photo123"
        test_path = "/photos/test.jpg"

        mock_photo = Mock()
        mock_photo.file_path = test_path
        mock_photo.file_extension = ".jpg"
        mock_photo.filename = "test.jpg"

        with patch.object(PhotosRepository, "get_photo_by_id", new_callable=AsyncMock) as mock_get_photo:
            mock_get_photo.return_value = mock_photo

            with patch("pathlib.Path.exists", return_value=True):
                service = PhotosService(mock_db)

                # Act
                result = await service.get_photo_file_info(photo_id)

                # Assert
                assert result is not None
                assert str(result["file_path"]) == test_path
                assert result["media_type"] == "image/jpeg"
                assert result["filename"] == "test.jpg"

                mock_get_photo.assert_called_once_with(photo_id)

    @pytest.mark.asyncio
    async def test_get_photo_file_info_photo_not_found(self, mock_db):
        # Arrange
        photo_id = "nonexistent"

        with patch.object(PhotosRepository, "get_photo_by_id", new_callable=AsyncMock) as mock_get_photo:
            mock_get_photo.return_value = None

            service = PhotosService(mock_db)

            # Act
            result = await service.get_photo_file_info(photo_id)

            # Assert
            assert result is None
            mock_get_photo.assert_called_once_with(photo_id)

    @pytest.mark.asyncio
    async def test_get_photo_file_info_file_not_exists(self, mock_db):
        # Arrange
        photo_id = "photo123"
        test_path = "/photos/nonexistent.jpg"

        mock_photo = Mock()
        mock_photo.file_path = test_path
        mock_photo.file_extension = ".jpg"
        mock_photo.filename = "test.jpg"

        with patch.object(PhotosRepository, "get_photo_by_id", new_callable=AsyncMock) as mock_get_photo:
            mock_get_photo.return_value = mock_photo

            with patch("pathlib.Path.exists", return_value=False):
                service = PhotosService(mock_db)

                # Act
                result = await service.get_photo_file_info(photo_id)

                # Assert
                assert result is None
                mock_get_photo.assert_called_once_with(photo_id)

    @pytest.mark.asyncio
    async def test_get_photo_file_info_different_media_types(self, mock_db):
        # Test different file extensions to verify media type mapping
        test_cases = [
            (".jpg", "image/jpeg"),
            (".jpeg", "image/jpeg"),
            (".png", "image/png"),
            (".webp", "image/webp"),
            (".gif", "image/gif"),
            (".bmp", "image/bmp"),
            (".tiff", "image/tiff"),
            (".tif", "image/tiff"),
            (".JPG", "image/jpeg"),  # Test case insensitive
            (".PNG", "image/png"),  # Test case insensitive
            (".xyz", "application/octet-stream"),  # Unknown extension
            ("", "application/octet-stream"),  # Empty extension
        ]

        for extension, expected_media_type in test_cases:
            # Arrange
            photo_id = f"photo_{extension}"
            test_path = f"/photos/test{extension}"

            mock_photo = Mock()
            mock_photo.file_path = test_path
            mock_photo.file_extension = extension
            mock_photo.filename = f"test{extension}"

            with patch.object(PhotosRepository, "get_photo_by_id", new_callable=AsyncMock) as mock_get_photo:
                mock_get_photo.return_value = mock_photo

                with patch("pathlib.Path.exists", return_value=True):
                    service = PhotosService(mock_db)

                    # Act
                    result = await service.get_photo_file_info(photo_id)

                    # Assert
                    assert result is not None
                    assert result["media_type"] == expected_media_type

    @pytest.mark.asyncio
    async def test_file_size_mb_rounding(self, mock_db):
        # Arrange
        photo_id = "photo123"
        mock_photo = Mock()
        mock_photo.id = photo_id
        mock_photo.filename = "test.jpg"
        mock_photo.get_display_title.return_value = "Test Photo"
        mock_photo.category = "nature"
        mock_photo.file_path = "/photos/nature/test.jpg"
        mock_photo.width = 1920
        mock_photo.height = 1080
        mock_photo.aspect_ratio = 1.78
        mock_photo.orientation = "landscape"
        mock_photo.megapixels = 2.07
        mock_photo.file_size = 2621440
        mock_photo.file_size_mb = 2.567891  # Test rounding
        mock_photo.file_extension = ".jpg"
        mock_photo.created_at = "2024-01-01T00:00:00"
        mock_photo.updated_at = "2024-01-01T00:00:00"
        mock_photo.file_modified_at = "2024-01-01T00:00:00"

        with patch.object(PhotosRepository, "get_photo_by_id", new_callable=AsyncMock) as mock_get_photo:
            mock_get_photo.return_value = mock_photo

            service = PhotosService(mock_db)

            # Act
            result = await service.get_photo_by_id(photo_id)

            # Assert
            assert result is not None
            assert result["file_size_mb"] == 2.57  # Should be rounded to 2 decimal places
            mock_get_photo.assert_called_once_with(photo_id)
