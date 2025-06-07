from datetime import datetime
from pathlib import Path
from uuid import uuid4

from sqlalchemy import BigInteger, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from pgs_db.database import Base


class Photo(Base):
    __tablename__ = "photos"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid4()))

    # File information
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False, unique=True)
    category: Mapped[str] = mapped_column(String(100), nullable=False)  # "cars", "cosplay", etc.

    # Basic metadata
    title: Mapped[str | None] = mapped_column(String(200))
    file_size: Mapped[int] = mapped_column(BigInteger, nullable=False)
    width: Mapped[int | None] = mapped_column(Integer)
    height: Mapped[int | None] = mapped_column(Integer)

    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    file_modified_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    def __repr__(self) -> str:
        return f"<Photo(id={self.id!r}, filename={self.filename!r}, category={self.category!r})>"

    @property
    def file_extension(self) -> str:
        """Get the file extension in lowercase."""
        return Path(self.filename).suffix.lower()

    @property
    def name_without_extension(self) -> str:
        """Get the filename without extension."""
        return Path(self.filename).stem

    @property
    def aspect_ratio(self) -> float | None:
        """Calculate the aspect ratio (width/height) if dimensions are available."""
        if self.width and self.height:
            return self.width / self.height
        return None

    @property
    def orientation(self) -> str | None:
        """Determine photo orientation: 'landscape', 'portrait', or 'square'."""
        if self.width and self.height:
            if self.width > self.height:
                return "landscape"
            elif self.height > self.width:
                return "portrait"
            else:
                return "square"
        return None

    @property
    def megapixels(self) -> float | None:
        """Calculate megapixels if dimensions are available."""
        if self.width and self.height:
            return (self.width * self.height) / 1_000_000
        return None

    @property
    def file_size_mb(self) -> float:
        """Get file size in megabytes."""
        return self.file_size / (1024 * 1024)

    def is_image_format(self) -> bool:
        """Check if the file extension is a common image format."""
        image_extensions = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp", ".raw", ".cr2", ".nef", ".arw"}
        return self.file_extension in image_extensions

    def get_display_title(self) -> str:
        """Get the title for display, falling back to filename without extension."""
        return self.title or self.name_without_extension
