from config import get_settings
from database import get_session, get_engine


def test_session():
    settings = get_settings()
    settings.database_url = "sqlite:///:memory:"
    engine = get_engine(settings=settings)
    session_generator = get_session(engine)
    session = next(session_generator)

    print(session)
