import logging
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import NamedTuple

from PIL import Image
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from pgs_db.config import db_config
from pgs_db.database import db_manager
from pgs_db.models import Photo

logger = logging.getLogger(__name__)


class ImageMetadata(NamedTuple):
    """Container for extracted image metadata."""

    file_size: int
    width: int | None
    height: int | None
    file_modified_at: datetime


class SyncStats(NamedTuple):
    """Statistics from a sync operation."""

    files_scanned: int
    files_added: int
    files_updated: int
    files_removed: int
    errors: int


# Supported image file extensions
SUPPORTED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".webp",
    ".bmp",
    ".tiff",
    ".tif",
    ".raw",
    ".cr2",
    ".nef",
    ".arw",
    ".dng",
    ".orf",
    ".rw2",
    ".pef",
    ".srw",
}


def extract_image_metadata(file_path: Path) -> ImageMetadata:
    """Extract basic metadata from an image file.

    Args:
        file_path: Path to the image file

    Returns:
        ImageMetadata with file size, dimensions, and modification time

    Raises:
        OSError: If file cannot be accessed
        Exception: If image cannot be processed
    """
    # Get file stats
    stat = file_path.stat()
    file_size = stat.st_size
    file_modified_at = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)

    width = None
    height = None

    # Try to extract image dimensions
    # Some raw formats may not be supported by Pillow
    try:
        with Image.open(file_path) as img:
            width, height = img.size
    except Exception as e:
        logger.debug(f"Could not extract dimensions from {file_path}: {e}")
        # For raw files or unsupported formats, we'll just store None for dimensions

    return ImageMetadata(file_size=file_size, width=width, height=height, file_modified_at=file_modified_at)


def generate_title_from_filename(filename: str) -> str:
    """Generate a human-readable title from a filename.

    Args:
        filename: The original filename (with or without extension)

    Returns:
        A cleaned-up title suitable for display
    """
    # Remove file extension
    name = Path(filename).stem

    # Remove common photo prefixes (IMG_, DSC_, etc.)
    name = re.sub(r"^(IMG|DSC|DSCN|P|PIC|PHOTO|IMAGE)[-_]?", "", name, flags=re.IGNORECASE)

    # Remove timestamp patterns (YYYYMMDD, YYYY-MM-DD, etc.)
    name = re.sub(r"\b\d{4}[-_]?\d{2}[-_]?\d{2}\b", "", name)
    name = re.sub(r"\b\d{8}\b", "", name)

    # Remove time patterns (HHMMSS, HH-MM-SS, etc.)
    name = re.sub(r"\b\d{2}[-_:]?\d{2}[-_:]?\d{2}\b", "", name)

    # Remove sequential numbers at start or end
    name = re.sub(r"^[-_]?\d+[-_]?", "", name)
    name = re.sub(r"[-_]?\d+[-_]?$", "", name)

    # Replace underscores and hyphens with spaces
    name = re.sub(r"[-_]+", " ", name)

    # Clean up multiple spaces
    name = re.sub(r"\s+", " ", name)

    # Capitalize words
    name = name.strip().title()

    # If we ended up with an empty string, use the original stem
    if not name:
        name = Path(filename).stem.replace("_", " ").replace("-", " ").title()

    return name


def __is_supported_image_file(file_path: Path) -> bool:
    """Check if a file is a supported image format.

    Args:
        file_path: Path to check

    Returns:
        True if the file extension is supported
    """
    return file_path.suffix.lower() in SUPPORTED_EXTENSIONS


async def __get_existing_photos_by_path(session: AsyncSession) -> dict[str, Photo]:
    """Get all existing photos indexed by their file path.

    Args:
        session: Database session

    Returns:
        Dictionary mapping file paths to Photo objects
    """
    result = await session.execute(select(Photo))
    photos = result.scalars().all()
    return {photo.file_path: photo for photo in photos}


async def sync_filesystem_to_db(storage_path: Path | str | None = None) -> SyncStats:
    """Scan storage directory and update database with photo metadata.

    This function:
    1. Scans the storage directory for image files
    2. Extracts metadata from new or changed files
    3. Updates the database with new photos
    4. Removes database entries for deleted files

    Args:
        storage_path: Path to the storage directory. If None, uses configured photos path.

    Returns:
        SyncStats with operation statistics

    Raises:
        FileNotFoundError: If storage directory doesn't exist
        RuntimeError: If database is not initialized
    """
    if storage_path is None:
        storage_path = db_config.photos_base_path
    else:
        storage_path = Path(storage_path)

    if not storage_path.exists():
        raise FileNotFoundError(f"Storage directory not found: {storage_path}")

    if not storage_path.is_dir():
        raise ValueError(f"Storage path is not a directory: {storage_path}")

    logger.info(f"Starting filesystem sync for {storage_path}")

    stats = SyncStats(files_scanned=0, files_added=0, files_updated=0, files_removed=0, errors=0)

    async with db_manager.get_session() as session:
        # Get existing photos to compare against
        existing_photos = await __get_existing_photos_by_path(session)
        found_file_paths = set()

        # Scan storage directory
        for category_dir in storage_path.iterdir():
            if not category_dir.is_dir():
                continue

            category_name = category_dir.name
            logger.debug(f"Scanning category: {category_name}")

            # Scan all image files in the category directory
            for image_file in category_dir.iterdir():
                if not image_file.is_file() or not __is_supported_image_file(image_file):
                    continue

                file_path_str = str(image_file.resolve())
                found_file_paths.add(file_path_str)
                stats = stats._replace(files_scanned=stats.files_scanned + 1)

                try:
                    # Check if a photo already exists in the database
                    existing_photo = existing_photos.get(file_path_str)

                    # Extract metadata
                    metadata = extract_image_metadata(image_file)

                    if existing_photo is None:
                        # Add a new photo
                        title = generate_title_from_filename(image_file.name)

                        new_photo = Photo(
                            filename=image_file.name,
                            file_path=file_path_str,
                            category=category_name,
                            title=title,
                            file_size=metadata.file_size,
                            width=metadata.width,
                            height=metadata.height,
                            file_modified_at=metadata.file_modified_at,
                        )

                        session.add(new_photo)
                        stats = stats._replace(files_added=stats.files_added + 1)
                        logger.debug(f"Added new photo: {image_file.name}")

                    else:
                        # Check if a file was modified since last sync
                        if existing_photo.file_modified_at != metadata.file_modified_at:
                            # Update an existing photo
                            existing_photo.filename = image_file.name
                            existing_photo.category = category_name
                            existing_photo.file_size = metadata.file_size
                            existing_photo.width = metadata.width
                            existing_photo.height = metadata.height
                            existing_photo.file_modified_at = metadata.file_modified_at

                            # Regenerate title if it wasn't manually set
                            if not existing_photo.title or existing_photo.title == generate_title_from_filename(
                                existing_photo.filename
                            ):
                                existing_photo.title = generate_title_from_filename(image_file.name)

                            stats = stats._replace(files_updated=stats.files_updated + 1)
                            logger.debug(f"Updated photo: {image_file.name}")

                except Exception as e:
                    logger.error(f"Error processing {image_file}: {e}")
                    stats = stats._replace(errors=stats.errors + 1)
                    continue

        # Remove database entries for files that no longer exist
        orphaned_photos = [photo for file_path, photo in existing_photos.items() if file_path not in found_file_paths]

        if orphaned_photos:
            orphaned_ids = [photo.id for photo in orphaned_photos]
            await session.execute(delete(Photo).where(Photo.id.in_(orphaned_ids)))
            stats = stats._replace(files_removed=len(orphaned_photos))
            logger.info(f"Removed {len(orphaned_photos)} orphaned photo records")

        # Commit all changes
        await session.commit()

    logger.info(
        f"Sync completed: {stats.files_scanned} scanned, "
        f"{stats.files_added} added, {stats.files_updated} updated, "
        f"{stats.files_removed} removed, {stats.errors} errors"
    )

    return stats


async def remove_orphaned_photos() -> int:
    """Remove database entries for files that no longer exist on disk.

    Returns:
        Number of orphaned photos removed
    """
    async with db_manager.get_session() as session:
        result = await session.execute(select(Photo))
        all_photos = result.scalars().all()

        orphaned_photos = []
        for photo in all_photos:
            if not Path(photo.file_path).exists():
                orphaned_photos.append(photo)

        if orphaned_photos:
            orphaned_ids = [photo.id for photo in orphaned_photos]
            await session.execute(delete(Photo).where(Photo.id.in_(orphaned_ids)))
            await session.commit()

            logger.info(f"Removed {len(orphaned_photos)} orphaned photo records")

        return len(orphaned_photos)
