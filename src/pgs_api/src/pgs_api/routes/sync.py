import logging

from fastapi import APIRouter, HTTPException, Depends
from starlette.status import HTTP_200_OK

from pgs_api.services.sync import SyncService, SyncStats

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sync", tags=["sync"])


@router.post("", response_model=SyncStats, status_code=HTTP_200_OK)
async def sync_photos(sync_service: SyncService = Depends(SyncService)) -> SyncStats:
    """Scan filesystem and update database with photo metadata."""
    try:
        return await sync_service.sync_photos()
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error during sync: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Sync operation failed")
