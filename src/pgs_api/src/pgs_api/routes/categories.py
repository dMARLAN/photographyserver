from fastapi import APIRouter, HTTPException

from pgs_api.dependencies import DatabaseSession
from pgs_api.services.categories import CategoriesService

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("")
async def list_categories(db: DatabaseSession):
    """List all available photo categories."""
    service = CategoriesService(db)
    categories = await service.list_categories()
    return {"categories": categories}


@router.get("/{category}")
async def list_photos_in_category(category: str, db: DatabaseSession):
    """List all photos in a specific category."""
    service = CategoriesService(db)
    photos = await service.get_photos_in_category(category)

    if not photos:
        raise HTTPException(status_code=404, detail=f"Category '{category}' not found or empty")

    return {
        "category": category,
        "photos": photos,
    }
