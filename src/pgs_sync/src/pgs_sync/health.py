"""Health monitoring server for the sync worker."""

from __future__ import annotations

import logging
from collections import deque
from datetime import datetime, timezone
from typing import Callable

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from pgs_db.database import DatabaseManager
from pgs_sync.types import FileEventType, SyncStats

logger = logging.getLogger(__name__)


class HealthMonitor:
    """Health monitoring and statistics for the sync worker."""

    def __init__(
        self,
        db_manager: DatabaseManager | None = None,
        watcher_observer: object | None = None,
        get_queue_size: Callable[[], int] | None = None,
    ) -> None:
        self.app = FastAPI(title="PGS Sync Worker Health Monitor")
        self.start_time = datetime.now(timezone.utc)
        self.db_manager = db_manager
        self.watcher_observer = watcher_observer
        self.get_queue_size = get_queue_size

        # Initialize daily stats tracking
        self._current_date = datetime.now(timezone.utc).date()
        self._daily_stats_reset()

        # Track processing times (keep last 1000 for running average)
        self._processing_times: deque[float] = deque(maxlen=1000)

        # Overall stats
        self.total_processed_events = 0
        self.total_failed_events = 0
        self.last_sync: datetime | None = None
        self.last_full_sync: datetime | None = None

        self._setup_routes()

    def _daily_stats_reset(self) -> None:
        """Reset daily statistics counters."""
        self.files_processed_today = 0
        self.files_added_today = 0
        self.files_updated_today = 0
        self.files_removed_today = 0

    def _check_daily_reset(self) -> None:
        """Check if we need to reset daily counters."""
        current_date = datetime.now(timezone.utc).date()
        if current_date != self._current_date:
            logger.info(f"Resetting daily statistics for new day: {current_date}")
            self._current_date = current_date
            self._daily_stats_reset()

    def _setup_routes(self) -> None:
        """Set up health check and statistics endpoints."""

        @self.app.get("/health")
        async def health_check() -> JSONResponse:
            """Health check endpoint for Docker health checks."""
            self._check_daily_reset()

            uptime = int((datetime.now(timezone.utc) - self.start_time).total_seconds())

            # Check database connectivity
            database_connected = await self._check_database_connectivity()

            # Check watcher status
            watcher_active = self._check_watcher_status()

            # Determine overall health status
            status = "healthy" if database_connected and watcher_active else "unhealthy"

            return JSONResponse(
                content={
                    "status": status,
                    "uptime": uptime,
                    "last_sync": self.last_sync.isoformat() if self.last_sync else None,
                    "database_connected": database_connected,
                    "watcher_active": watcher_active,
                }
            )

        @self.app.get("/stats")
        async def get_statistics() -> JSONResponse:
            """Get detailed statistics about the sync worker."""
            self._check_daily_reset()

            uptime = int((datetime.now(timezone.utc) - self.start_time).total_seconds())
            pending_events = self.get_queue_size() if self.get_queue_size else 0
            average_processing_time = self._calculate_average_processing_time()

            return JSONResponse(
                content={
                    "sync_statistics": {
                        "files_processed_today": self.files_processed_today,
                        "files_added_today": self.files_added_today,
                        "files_updated_today": self.files_updated_today,
                        "files_removed_today": self.files_removed_today,
                        "last_full_sync": (self.last_full_sync.isoformat() if self.last_full_sync else None),
                        "average_processing_time_ms": average_processing_time,
                    },
                    "event_queue": {
                        "pending_events": pending_events,
                        "processed_events": self.total_processed_events,
                        "failed_events": self.total_failed_events,
                    },
                    "uptime": uptime,
                }
            )

    def update_stats(self, **kwargs: object) -> None:  # type: ignore[misc]
        """Update worker statistics.

        Args:
            **kwargs: Supported keyword arguments:
                - processed_events: Number of events successfully processed
                - failed_events: Number of events that failed processing
                - last_sync: Timestamp of last sync operation
                - last_full_sync: Timestamp of last full sync operation
                - processing_time_ms: Processing time in milliseconds for performance tracking
                - sync_stats: SyncStats object from full sync operations
                - event_types: List of FileEventType for processed events
        """
        self._check_daily_reset()

        # Update event counters
        if "processed_events" in kwargs and isinstance(kwargs["processed_events"], int):
            count = kwargs["processed_events"]
            self.total_processed_events += count
            self.files_processed_today += count

        if "failed_events" in kwargs and isinstance(kwargs["failed_events"], int):
            count = kwargs["failed_events"]
            self.total_failed_events += count

        # Update sync timestamps
        if "last_sync" in kwargs:
            if isinstance(kwargs["last_sync"], (int, float)):
                self.last_sync = datetime.fromtimestamp(kwargs["last_sync"], timezone.utc)
            elif isinstance(kwargs["last_sync"], datetime):
                self.last_sync = kwargs["last_sync"]

        if "last_full_sync" in kwargs:
            if isinstance(kwargs["last_full_sync"], (int, float)):
                self.last_full_sync = datetime.fromtimestamp(kwargs["last_full_sync"], timezone.utc)
            elif isinstance(kwargs["last_full_sync"], datetime):
                self.last_full_sync = kwargs["last_full_sync"]

        # Track processing times for performance monitoring
        if "processing_time_ms" in kwargs and isinstance(kwargs["processing_time_ms"], (int, float)):
            self._processing_times.append(float(kwargs["processing_time_ms"]))

        # Update daily stats from sync operations
        if "sync_stats" in kwargs and isinstance(kwargs["sync_stats"], SyncStats):
            sync_stats = kwargs["sync_stats"]
            self.files_added_today += sync_stats.files_added
            self.files_updated_today += sync_stats.files_updated
            self.files_removed_today += sync_stats.files_removed
            self.files_processed_today += sync_stats.files_scanned
            self.last_full_sync = datetime.now(timezone.utc)

        # Update daily stats from individual event types
        if "event_types" in kwargs:
            event_types = kwargs["event_types"]
            if isinstance(event_types, list):
                for event_type in event_types:
                    if event_type == FileEventType.CREATED:
                        self.files_added_today += 1
                    elif event_type == FileEventType.MODIFIED:
                        self.files_updated_today += 1
                    elif event_type == FileEventType.DELETED:
                        self.files_removed_today += 1

    async def _check_database_connectivity(self) -> bool:
        """Check if database is accessible and responsive.

        Returns:
            True if database is healthy, False otherwise
        """
        if not self.db_manager:
            logger.warning("Database manager not provided to health monitor")
            return False

        try:
            health_result = await self.db_manager.health_check()
            return health_result.get("status") == "healthy"
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False

    def _check_watcher_status(self) -> bool:
        """Check if file system watcher is active.

        Returns:
            True if watcher is running, False otherwise
        """
        if not self.watcher_observer:
            logger.warning("Watcher observer not provided to health monitor")
            return False

        try:
            # Check if observer is alive and running
            if hasattr(self.watcher_observer, "is_alive"):
                return self.watcher_observer.is_alive()  # type: ignore
            return False
        except Exception as e:
            logger.error(f"Watcher status check failed: {e}")
            return False

    def _calculate_average_processing_time(self) -> float:
        """Calculate average processing time from recent samples.

        Returns:
            Average processing time in milliseconds
        """
        if not self._processing_times:
            return 0.0

        return sum(self._processing_times) / len(self._processing_times)

    def set_database_manager(self, db_manager: DatabaseManager) -> None:
        """Set the database manager for connectivity checks."""
        self.db_manager = db_manager

    def set_watcher_observer(self, observer: object | None) -> None:
        """Set the watcher observer for status checks."""
        self.watcher_observer = observer

    def set_queue_size_callback(self, callback: Callable[[], int]) -> None:
        """Set callback function to get current queue size."""
        self.get_queue_size = callback

    def get_app(self) -> FastAPI:
        """Get the FastAPI application for the health monitor."""
        return self.app
