from collections.abc import AsyncGenerator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from pgs_db.database import db_manager


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Get a database session for dependency injection.

    This dependency provides a database session that is automatically
    closed when the request is complete. It handles rollback on exceptions.

    Yields:
        AsyncSession: Database session for the request
    """
    async with db_manager.get_session() as session:
        yield session


# Type alias for database session dependency
DatabaseSession = Annotated[AsyncSession, Depends(get_db_session)]
