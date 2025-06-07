"""Tests for health monitoring functionality."""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi.testclient import TestClient

from pgs_sync.health import HealthMonitor
from pgs_sync.types import FileEventType, SyncStats


class TestHealthMonitor:
    """Test the HealthMonitor class."""

    @pytest.fixture
    def mock_db_manager(self) -> MagicMock:
        """Create a mock database manager."""
        db_manager = MagicMock()
        db_manager.health_check = AsyncMock(return_value={"status": "healthy"})
        return db_manager

    @pytest.fixture
    def mock_watcher_observer(self) -> MagicMock:
        """Create a mock watcher observer."""
        observer = MagicMock()
        observer.is_alive.return_value = True
        return observer

    @pytest.fixture
    def mock_queue_size_callback(self) -> MagicMock:
        """Create a mock callback for getting queue size."""
        callback = MagicMock(return_value=5)
        return callback

    @pytest.fixture
    def health_monitor(self, mock_db_manager, mock_watcher_observer, mock_queue_size_callback) -> HealthMonitor:
        """Create a HealthMonitor for testing."""
        return HealthMonitor(
            db_manager=mock_db_manager, watcher_observer=mock_watcher_observer, get_queue_size=mock_queue_size_callback
        )

    @pytest.fixture
    def test_client(self, health_monitor: HealthMonitor) -> TestClient:
        """Create a test client for the health monitor app."""
        return TestClient(health_monitor.get_app())

    @pytest.mark.unit
    def test_initialization(self, health_monitor: HealthMonitor):
        """Test that HealthMonitor is initialized correctly."""
        assert health_monitor.app is not None
        assert health_monitor.start_time is not None
        assert isinstance(health_monitor.start_time, datetime)
        assert health_monitor.start_time.tzinfo == timezone.utc

        # Check initial statistics
        assert health_monitor.files_processed_today == 0
        assert health_monitor.files_added_today == 0
        assert health_monitor.files_updated_today == 0
        assert health_monitor.files_removed_today == 0
        assert health_monitor.total_processed_events == 0
        assert health_monitor.total_failed_events == 0
        assert health_monitor.last_sync is None
        assert health_monitor.last_full_sync is None

    @pytest.mark.unit
    def test_daily_stats_reset(self, health_monitor: HealthMonitor):
        """Test that daily statistics are reset correctly."""
        # Set some stats
        health_monitor.files_processed_today = 10
        health_monitor.files_added_today = 5
        health_monitor.files_updated_today = 3
        health_monitor.files_removed_today = 2

        # Reset stats
        health_monitor._daily_stats_reset()

        assert health_monitor.files_processed_today == 0
        assert health_monitor.files_added_today == 0
        assert health_monitor.files_updated_today == 0
        assert health_monitor.files_removed_today == 0

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_health_endpoint_healthy(self, test_client: TestClient):
        """Test health endpoint when all systems are healthy."""
        response = test_client.get("/health")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "healthy"
        assert "uptime" in data
        assert data["database_connected"] is True
        assert data["watcher_active"] is True
        assert "last_sync" in data

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_health_endpoint_unhealthy_database(self, health_monitor: HealthMonitor):
        """Test health endpoint when database is unhealthy."""
        # Mock database health check to fail
        health_monitor.db_manager.health_check = AsyncMock(return_value={"status": "unhealthy"})

        test_client = TestClient(health_monitor.get_app())
        response = test_client.get("/health")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "unhealthy"
        assert data["database_connected"] is False

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_health_endpoint_unhealthy_watcher(self, health_monitor: HealthMonitor):
        """Test health endpoint when watcher is inactive."""
        # Mock watcher to be inactive
        health_monitor.watcher_observer.is_alive.return_value = False

        test_client = TestClient(health_monitor.get_app())
        response = test_client.get("/health")

        assert response.status_code == 200
        data = response.json()

        assert data["status"] == "unhealthy"
        assert data["watcher_active"] is False

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_stats_endpoint(self, test_client: TestClient):
        """Test statistics endpoint."""
        response = test_client.get("/stats")

        assert response.status_code == 200
        data = response.json()

        # Check structure
        assert "sync_statistics" in data
        assert "event_queue" in data
        assert "uptime" in data

        # Check sync statistics
        sync_stats = data["sync_statistics"]
        assert "files_processed_today" in sync_stats
        assert "files_added_today" in sync_stats
        assert "files_updated_today" in sync_stats
        assert "files_removed_today" in sync_stats
        assert "last_full_sync" in sync_stats
        assert "average_processing_time_ms" in sync_stats

        # Check event queue statistics
        event_queue = data["event_queue"]
        assert "pending_events" in event_queue
        assert "processed_events" in event_queue
        assert "failed_events" in event_queue
        assert event_queue["pending_events"] == 5  # From mock

    @pytest.mark.unit
    def test_update_stats_processed_events(self, health_monitor: HealthMonitor):
        """Test updating processed events statistics."""
        health_monitor.update_stats(processed_events=10)

        assert health_monitor.total_processed_events == 10
        assert health_monitor.files_processed_today == 10

    @pytest.mark.unit
    def test_update_stats_failed_events(self, health_monitor: HealthMonitor):
        """Test updating failed events statistics."""
        health_monitor.update_stats(failed_events=5)

        assert health_monitor.total_failed_events == 5

    @pytest.mark.unit
    def test_update_stats_timestamps(self, health_monitor: HealthMonitor):
        """Test updating timestamp statistics."""
        now = datetime.now(timezone.utc)

        health_monitor.update_stats(last_sync=now, last_full_sync=now)

        assert health_monitor.last_sync == now
        assert health_monitor.last_full_sync == now

    @pytest.mark.unit
    def test_update_stats_timestamp_from_number(self, health_monitor: HealthMonitor):
        """Test updating timestamps from numeric values."""
        timestamp = 1640995200.0  # 2022-01-01 00:00:00 UTC

        health_monitor.update_stats(last_sync=timestamp, last_full_sync=timestamp)

        expected = datetime.fromtimestamp(timestamp, timezone.utc)
        assert health_monitor.last_sync == expected
        assert health_monitor.last_full_sync == expected

    @pytest.mark.unit
    def test_update_stats_processing_time(self, health_monitor: HealthMonitor):
        """Test updating processing time statistics."""
        health_monitor.update_stats(processing_time_ms=50.5)
        health_monitor.update_stats(processing_time_ms=75.2)
        health_monitor.update_stats(processing_time_ms=60.1)

        avg = health_monitor._calculate_average_processing_time()
        expected_avg = (50.5 + 75.2 + 60.1) / 3
        assert abs(avg - expected_avg) < 0.01

    @pytest.mark.unit
    def test_update_stats_sync_stats(self, health_monitor: HealthMonitor):
        """Test updating statistics from SyncStats object."""
        sync_stats = SyncStats(files_scanned=100, files_added=10, files_updated=5, files_removed=2, errors=1)

        health_monitor.update_stats(sync_stats=sync_stats)

        assert health_monitor.files_added_today == 10
        assert health_monitor.files_updated_today == 5
        assert health_monitor.files_removed_today == 2
        assert health_monitor.files_processed_today == 100
        assert health_monitor.last_full_sync is not None

    @pytest.mark.unit
    def test_update_stats_event_types(self, health_monitor: HealthMonitor):
        """Test updating statistics from event types."""
        event_types = [
            FileEventType.CREATED,
            FileEventType.CREATED,
            FileEventType.MODIFIED,
            FileEventType.DELETED,
        ]

        health_monitor.update_stats(event_types=event_types)

        assert health_monitor.files_added_today == 2  # 2 CREATED events
        assert health_monitor.files_updated_today == 1  # 1 MODIFIED event
        assert health_monitor.files_removed_today == 1  # 1 DELETED event

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_check_database_connectivity_success(self, health_monitor: HealthMonitor):
        """Test successful database connectivity check."""
        result = await health_monitor._check_database_connectivity()
        assert result is True

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_check_database_connectivity_failure(self, health_monitor: HealthMonitor):
        """Test failed database connectivity check."""
        health_monitor.db_manager.health_check = AsyncMock(side_effect=Exception("Connection failed"))

        result = await health_monitor._check_database_connectivity()
        assert result is False

    @pytest.mark.asyncio
    @pytest.mark.unit
    async def test_check_database_connectivity_no_manager(self):
        """Test database connectivity check with no database manager."""
        health_monitor = HealthMonitor(db_manager=None)

        result = await health_monitor._check_database_connectivity()
        assert result is False

    @pytest.mark.unit
    def test_check_watcher_status_active(self, health_monitor: HealthMonitor):
        """Test watcher status check when active."""
        result = health_monitor._check_watcher_status()
        assert result is True

    @pytest.mark.unit
    def test_check_watcher_status_inactive(self, health_monitor: HealthMonitor):
        """Test watcher status check when inactive."""
        health_monitor.watcher_observer.is_alive.return_value = False

        result = health_monitor._check_watcher_status()
        assert result is False

    @pytest.mark.unit
    def test_check_watcher_status_exception(self, health_monitor: HealthMonitor):
        """Test watcher status check with exception."""
        health_monitor.watcher_observer.is_alive.side_effect = Exception("Observer error")

        result = health_monitor._check_watcher_status()
        assert result is False

    @pytest.mark.unit
    def test_check_watcher_status_no_observer(self):
        """Test watcher status check with no observer."""
        health_monitor = HealthMonitor(watcher_observer=None)

        result = health_monitor._check_watcher_status()
        assert result is False

    @pytest.mark.unit
    def test_calculate_average_processing_time_empty(self, health_monitor: HealthMonitor):
        """Test average processing time calculation with no data."""
        avg = health_monitor._calculate_average_processing_time()
        assert avg == 0.0

    @pytest.mark.unit
    def test_calculate_average_processing_time_with_data(self, health_monitor: HealthMonitor):
        """Test average processing time calculation with data."""
        times = [10.0, 20.0, 30.0, 40.0, 50.0]
        for time_ms in times:
            health_monitor.update_stats(processing_time_ms=time_ms)

        avg = health_monitor._calculate_average_processing_time()
        expected = sum(times) / len(times)
        assert avg == expected

    @pytest.mark.unit
    def test_set_database_manager(self, health_monitor: HealthMonitor):
        """Test setting database manager."""
        new_db_manager = MagicMock()
        health_monitor.set_database_manager(new_db_manager)

        assert health_monitor.db_manager is new_db_manager

    @pytest.mark.unit
    def test_set_watcher_observer(self, health_monitor: HealthMonitor):
        """Test setting watcher observer."""
        new_observer = MagicMock()
        health_monitor.set_watcher_observer(new_observer)

        assert health_monitor.watcher_observer is new_observer

    @pytest.mark.unit
    def test_set_queue_size_callback(self, health_monitor: HealthMonitor):
        """Test setting queue size callback."""
        new_callback = MagicMock(return_value=10)
        health_monitor.set_queue_size_callback(new_callback)

        assert health_monitor.get_queue_size is new_callback
        assert health_monitor.get_queue_size() == 10

    @pytest.mark.unit
    def test_get_app(self, health_monitor: HealthMonitor):
        """Test getting the FastAPI application."""
        app = health_monitor.get_app()

        assert app is health_monitor.app
        assert app.title == "PGS Sync Worker Health Monitor"

    @pytest.mark.unit
    def test_daily_stats_reset_on_new_day(self, health_monitor: HealthMonitor):
        """Test that daily stats reset when crossing day boundary."""
        # Set some stats
        health_monitor.files_processed_today = 100
        health_monitor.files_added_today = 10

        # Mock current date to be different from initial date
        from unittest.mock import patch

        future_date = health_monitor._current_date.replace(day=health_monitor._current_date.day + 1)

        with patch("pgs_sync.health.datetime") as mock_datetime:
            mock_datetime.now.return_value.date.return_value = future_date
            health_monitor._check_daily_reset()

        # Stats should be reset
        assert health_monitor.files_processed_today == 0
        assert health_monitor.files_added_today == 0
        assert health_monitor._current_date == future_date
