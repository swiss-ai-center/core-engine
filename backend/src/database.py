from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlmodel import Session, create_engine
from config import Settings, get_settings

_engine = None


def get_engine(settings: Settings = Depends(get_settings)):
    """Get or create the database engine."""
    global _engine

    if _engine is None:
        _engine = create_engine(
            settings.database_url,
            connect_args=settings.database_connect_args,
            # echo=settings.environment == "development",  # Optional: log SQL in dev
        )

    return _engine


def get_session(engine=Depends(get_engine)):
    """Get a database session."""
    with Session(engine) as session:
        session.expire_on_commit = False
        yield session


def _to_async_url(url: str) -> str:
    """Derive the async driver URL from the sync database URL."""
    if url.startswith("sqlite:"):
        return url.replace("sqlite:", "sqlite+aiosqlite:", 1)
    if url.startswith("postgresql:"):
        return url.replace("postgresql:", "postgresql+asyncpg:", 1)
    return url


_async_engine = None


def get_async_engine(settings: Settings = Depends(get_settings)):
    """Get or create the async database engine (used by fastapi-users)."""
    global _async_engine

    if _async_engine is None:
        _async_engine = create_async_engine(_to_async_url(settings.database_url))

    return _async_engine


async def get_async_session(engine=Depends(get_async_engine)):
    """Get an async database session."""
    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield session
