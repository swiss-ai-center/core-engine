from fastapi import Depends
from sqlmodel import Session, SQLModel, create_engine
from config import Settings, get_settings
from sqlalchemy.orm import declarative_base

Base = declarative_base()


def initialize_db(settings: Settings = Depends(get_settings)):
    """Initialize the database connection."""
    Base.registry.configure()
    engine = create_engine(
        settings.database_url, connect_args=settings.database_connect_args
    )
    Base.metadata.create_all(engine)
    SQLModel.metadata.create_all(engine)

    return engine


def get_session(engine=Depends(initialize_db)):
    """Get a database session."""
    with Session(engine) as session:
        yield session
