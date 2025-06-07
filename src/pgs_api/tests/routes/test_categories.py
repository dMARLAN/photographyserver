import pytest
from unittest.mock import AsyncMock
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from pgs_api.routes import categories as categories_module
from pgs_api.routes.categories import list_categories, list_photos_in_category
from pgs_api.services.categories import CategoriesService


@pytest.fixture
def mock_db(mocker):
    return mocker.Mock(spec=AsyncSession)


@pytest.fixture
def mock_categories_service(mocker):
    return mocker.Mock(spec=CategoriesService)


class TestListCategories:
    @pytest.mark.asyncio
    async def test_list_categories_success(self, mock_db, mock_categories_service, mocker):
        # Arrange
        expected_categories = [
            {"name": "nature", "photo_count": 5, "latest_photo": "2024-01-01T00:00:00"},
            {"name": "portraits", "photo_count": 3, "latest_photo": "2024-01-02T00:00:00"},
        ]
        mock_categories_service.list_categories = AsyncMock(return_value=expected_categories)
        mocker.patch.object(categories_module, "CategoriesService", return_value=mock_categories_service)

        # Act
        result = await list_categories(mock_db)

        # Assert
        assert result == {"categories": expected_categories}
        mock_categories_service.list_categories.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_categories_empty(self, mock_db, mock_categories_service, mocker):
        # Arrange
        mock_categories_service.list_categories = AsyncMock(return_value=[])
        mocker.patch.object(categories_module, "CategoriesService", return_value=mock_categories_service)

        # Act
        result = await list_categories(mock_db)

        # Assert
        assert result == {"categories": []}
        mock_categories_service.list_categories.assert_called_once()


class TestListPhotosInCategory:
    @pytest.mark.asyncio
    async def test_list_photos_in_category_success(self, mock_db, mock_categories_service, mocker):
        category = "nature"
        expected_photos = [
            {
                "id": "photo1",
                "filename": "sunset.jpg",
                "title": "Beautiful Sunset",
                "width": 1920,
                "height": 1080,
                "aspect_ratio": 1.78,
                "orientation": "landscape",
                "file_size_mb": 2.5,
                "url": "/api/v1/photos/photo1/file",
                "created_at": "2024-01-01T00:00:00",
                "file_modified_at": "2024-01-01T00:00:00",
            }
        ]

        # Arrange
        mock_categories_service.get_photos_in_category = AsyncMock(return_value=expected_photos)
        mocker.patch.object(categories_module, "CategoriesService", return_value=mock_categories_service)

        # Act
        result = await list_photos_in_category(category, mock_db)

        assert result == {"category": category, "photos": expected_photos}
        mock_categories_service.get_photos_in_category.assert_called_once_with(category)

    @pytest.mark.asyncio
    async def test_list_photos_in_category_not_found(self, mock_db, mock_categories_service, mocker):
        category = "nonexistent"
        # Arrange
        mock_categories_service.get_photos_in_category = AsyncMock(return_value=None)
        mocker.patch.object(categories_module, "CategoriesService", return_value=mock_categories_service)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await list_photos_in_category(category, mock_db)

        assert exc_info.value.status_code == 404
        assert f"Category '{category}' not found or empty" in str(exc_info.value.detail)
        mock_categories_service.get_photos_in_category.assert_called_once_with(category)

    @pytest.mark.asyncio
    async def test_list_photos_in_category_empty(self, mock_db, mock_categories_service, mocker):
        category = "empty_category"
        # Arrange
        mock_categories_service.get_photos_in_category = AsyncMock(return_value=[])
        mocker.patch.object(categories_module, "CategoriesService", return_value=mock_categories_service)

        # Act & Assert
        with pytest.raises(HTTPException) as exc_info:
            await list_photos_in_category(category, mock_db)

        assert exc_info.value.status_code == 404
        assert f"Category '{category}' not found or empty" in str(exc_info.value.detail)
        mock_categories_service.get_photos_in_category.assert_called_once_with(category)
