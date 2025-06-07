from dataclasses import dataclass
from enum import StrEnum, auto


class DBStatus(StrEnum):
    HEALTHY = auto()
    UNHEALTHY = auto()


@dataclass(frozen=True)
class APIStatus:
    version: str
    environment: str


@dataclass(frozen=True)
class HealthCheck:
    """Health check status for the API."""

    db_status: DBStatus
    api_status: APIStatus
