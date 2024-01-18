from config import get_settings
from database import get_session, initialize_db


def test_session():
    settings = get_settings()
    settings.database_url = "sqlite:///:memory:"
    engine = initialize_db(settings=settings)
    session_generator = get_session(engine)
    session = next(session_generator)

    print(session)
