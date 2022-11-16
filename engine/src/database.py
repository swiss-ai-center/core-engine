from fastapi import Depends
from sqlmodel import Field, Session, SQLModel, create_engine
import config


def initialize_db(settings: config.Settings = Depends(config.get_settings)):
    engine = create_engine(
        settings.database_url, connect_args=settings.database_connect_args
    )

    SQLModel.metadata.create_all(engine)

    return engine


def get_session(engine=Depends(initialize_db)):
    with Session(engine) as session:
        yield session
