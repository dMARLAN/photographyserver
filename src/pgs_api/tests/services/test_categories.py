from unittest.mock import AsyncMock, Mock, patch

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from pgs_api.repositories.categories import CategoriesRepository
from pgs_api.services.categories import CategoriesService


@pytest.fixture
def mock_db():
    return Mock(spec=AsyncSession)


class TestCategoriesService:
    @pytest.mark.asyncio
    async def test_list_categories_success(self, mock_db) -> None:
        with patch.object(CategoriesRepository, "get_categories_with_stats", new_callable=AsyncMock) as mock_get_stats:
            mock_get_stats.return_value = [
                ("nature", 5, "2024-01-01T00:00:00"),
                ("portraits", 3, "2024-01-02T00:00:00"),
                ("street", 2, "2024-01-03T00:00:00"),
            ]

            service = CategoriesService(mock_db)

            result = await service.list_categories()

            assert len(result) == 3
            assert result[0] == {"name": "nature", "photo_count": 5, "latest_photo": "2024-01-01T00:00:00"}
            assert result[1] == {"name": "portraits", "photo_count": 3, "latest_photo": "2024-01-02T00:00:00"}
            assert result[2] == {"name": "street", "photo_count": 2, "latest_photo": "2024-01-03T00:00:00"}
            mock_get_stats.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_categories_empty(self, mock_db) -> None:
        with patch.object(CategoriesRepository, "get_categories_with_stats", new_callable=AsyncMock) as mock_get_stats:
            mock_get_stats.return_value = []

            service = CategoriesService(mock_db)

            result = await service.list_categories()

            assert result == []
            mock_get_stats.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_photos_in_category_success(self, mock_db) -> None:
        category = "nature"
        mock_photo = Mock()
        mock_photo.id = "photo1"
        mock_photo.filename = "sunset.jpg"
        mock_photo.get_display_title.return_value = "Beautiful Sunset"
        mock_photo.width = 1920
        mock_photo.height = 1080
        mock_photo.aspect_ratio = 1.78
        mock_photo.orientation = "landscape"
        mock_photo.file_size_mb = 2.5
        mock_photo.created_at = "2024-01-01T00:00:00"
        mock_photo.file_modified_at = "2024-01-01T00:00:00"

        with patch.object(CategoriesRepository, "get_photos_by_category", new_callable=AsyncMock) as mock_get_photos:
            mock_get_photos.return_value = [mock_photo]

            service = CategoriesService(mock_db)

            result = await service.get_photos_in_category(category)

            assert result is not None
            assert len(result) == 1
            photo = result[0]
            assert photo["id"] == "photo1"
            assert photo["filename"] == "sunset.jpg"
            assert photo["title"] == "Beautiful Sunset"
            assert photo["width"] == 1920
            assert photo["height"] == 1080
            assert photo["aspect_ratio"] == 1.78
            assert photo["orientation"] == "landscape"
            assert photo["file_size_mb"] == 2.5
            assert photo["url"] == "/api/v1/photos/photo1/file"
            assert photo["created_at"] == "2024-01-01T00:00:00"
            assert photo["file_modified_at"] == "2024-01-01T00:00:00"

            mock_get_photos.assert_called_once_with(category)
            mock_photo.get_display_title.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_photos_in_category_not_found(self, mock_db) -> None:
        category = "nonexistent"

        with patch.object(CategoriesRepository, "get_photos_by_category", new_callable=AsyncMock) as mock_get_photos:
            mock_get_photos.return_value = []

            service = CategoriesService(mock_db)

            result = await service.get_photos_in_category(category)

            assert result is None
            mock_get_photos.assert_called_once_with(category)

    @pytest.mark.asyncio
    async def test_get_photos_in_category_empty_list(self, mock_db) -> None:
        category = "empty"

        with patch.object(CategoriesRepository, "get_photos_by_category", new_callable=AsyncMock) as mock_get_photos:
            mock_get_photos.return_value = None

            service = CategoriesService(mock_db)

            result = await service.get_photos_in_category(category)

            assert result is None
            mock_get_photos.assert_called_once_with(category)

    @pytest.mark.asyncio
    async def test_get_photos_in_category_multiple_photos(self, mock_db) -> None:
        category = "nature"

        mock_photo1 = Mock()
        mock_photo1.id = "photo1"
        mock_photo1.filename = "sunset.jpg"
        mock_photo1.get_display_title.return_value = "Sunset"
        mock_photo1.width = 1920
        mock_photo1.height = 1080
        mock_photo1.aspect_ratio = 1.78
        mock_photo1.orientation = "landscape"
        mock_photo1.file_size_mb = 2.5
        mock_photo1.created_at = "2024-01-01T00:00:00"
        mock_photo1.file_modified_at = "2024-01-01T00:00:00"

        mock_photo2 = Mock()
        mock_photo2.id = "photo2"
        mock_photo2.filename = "tree.jpg"
        mock_photo2.get_display_title.return_value = "Old Tree"
        mock_photo2.width = 1080
        mock_photo2.height = 1920
        mock_photo2.aspect_ratio = 0.56
        mock_photo2.orientation = "portrait"
        mock_photo2.file_size_mb = 3.2
        mock_photo2.created_at = "2024-01-02T00:00:00"
        mock_photo2.file_modified_at = "2024-01-02T00:00:00"

        with patch.object(CategoriesRepository, "get_photos_by_category", new_callable=AsyncMock) as mock_get_photos:
            mock_get_photos.return_value = [mock_photo1, mock_photo2]

            service = CategoriesService(mock_db)

            result = await service.get_photos_in_category(category)

            assert result is not None
            assert len(result) == 2
            assert result[0]["id"] == "photo1"
            assert result[0]["filename"] == "sunset.jpg"
            assert result[1]["id"] == "photo2"
            assert result[1]["filename"] == "tree.jpg"

            mock_get_photos.assert_called_once_with(category)
            mock_photo1.get_display_title.assert_called_once()
            mock_photo2.get_display_title.assert_called_once()
