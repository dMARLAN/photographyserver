import logging

from fastapi import APIRouter, HTTPException

from pgs_api.services.sync import SyncService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sync", tags=["sync"])


@router.post("")
async def sync_photos():
    """Scan filesystem and update database with photo metadata."""
    try:
        result = await SyncService.sync_photos()
        return result
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error during sync: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Sync operation failed")
