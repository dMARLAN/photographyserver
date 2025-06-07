"""Utility functions for image processing and sync operations."""

import logging
import re
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image

from pgs_sync.types import ImageMetadata

logger = logging.getLogger(__name__)


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


def is_supported_image_file(file_path: Path, supported_extensions: set[str]) -> bool:
    """Check if a file is a supported image format.

    Args:
        file_path: Path to check
        supported_extensions: Set of supported file extensions

    Returns:
        True if the file extension is supported
    """
    return file_path.suffix.lower() in supported_extensions
