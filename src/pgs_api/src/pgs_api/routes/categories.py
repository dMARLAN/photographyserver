from fastapi import APIRouter, HTTPException
from sqlalchemy import select, func

from pgs_db.models import Photo
from pgs_api.dependencies import DatabaseSession

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("")
async def list_categories(db: DatabaseSession):
    """List all available photo categories."""
    # Get distinct categories from photos with counts and latest photo timestamp
    result = await db.execute(
        select(
            Photo.category, func.count(Photo.id).label("photo_count"), func.max(Photo.created_at).label("latest_photo")
        )
        .group_by(Photo.category)
        .order_by(Photo.category)
    )
    categories = result.all()

    return {
        "categories": [
            {"name": category, "photo_count": photo_count, "latest_photo": latest_photo}
            for category, photo_count, latest_photo in categories
        ]
    }


@router.get("/{category}")
async def list_photos_in_category(category: str, db: DatabaseSession):
    """List all photos in a specific category."""
    result = await db.execute(select(Photo).where(Photo.category == category).order_by(Photo.created_at.desc()))
    photos = result.scalars().all()

    if not photos:
        raise HTTPException(status_code=404, detail=f"Category '{category}' not found or empty")

    return {
        "category": category,
        "photos": [
            {
                "id": photo.id,
                "filename": photo.filename,
                "title": photo.get_display_title(),
                "width": photo.width,
                "height": photo.height,
                "aspect_ratio": photo.aspect_ratio,
                "orientation": photo.orientation,
                "file_size_mb": round(photo.file_size_mb, 2),
                "url": f"/api/v1/photos/{photo.id}/file",
                "created_at": photo.created_at,
                "file_modified_at": photo.file_modified_at,
            }
            for photo in photos
        ],
    }
