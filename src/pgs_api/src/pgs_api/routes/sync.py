import logging

from fastapi import APIRouter, HTTPException

from pgs_db.sync import sync_filesystem_to_db
from pgs_api.config import api_config

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sync", tags=["sync"])


@router.post("")
async def sync_photos():
    """Scan filesystem and update database with photo metadata."""
    try:
        stats = await sync_filesystem_to_db(api_config.storage_path)
        return {
            "message": "Sync completed successfully",
            "stats": {
                "files_scanned": stats.files_scanned,
                "files_added": stats.files_added,
                "files_updated": stats.files_updated,
                "files_removed": stats.files_removed,
                "errors": stats.errors,
            },
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error during sync: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Sync operation failed")
