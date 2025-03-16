"""Database configuration module."""

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite+aiosqlite:///keinonto.db"


async def create_engine() -> AsyncEngine:
    """Create a new database engine."""
    return create_async_engine(
        DATABASE_URL,
        echo=True,
    )


async def get_session() -> AsyncSession:
    """Create a new database session."""
    engine = await create_engine()
    session_factory = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )
    session = session_factory()
    try:
        yield session
    finally:
        await session.close()
        await engine.dispose()
