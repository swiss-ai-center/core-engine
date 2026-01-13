from fastapi import Depends
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
