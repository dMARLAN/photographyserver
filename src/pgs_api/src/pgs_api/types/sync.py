from dataclasses import dataclass


@dataclass(frozen=True)
class SyncStats:
    """Statistics for the sync operation."""

    files_scanned: int
    files_added: int
    files_updated: int
    files_removed: int
    errors: int
