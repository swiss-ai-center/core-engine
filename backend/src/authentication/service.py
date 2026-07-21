from uuid import UUID

from fastapi import Depends
from fastapi_users import BaseUserManager, UUIDIDMixin
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlmodel import Session, select

from authentication.models import Role, User
from config import Settings, get_settings
from database import get_async_session


async def get_user_db(session=Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)


class UserManager(UUIDIDMixin, BaseUserManager[User, UUID]):
    """
    fastapi-users manager: hashes passwords, verifies credentials on login
    and handles reset/verification token lifecycles.
    """

    def __init__(self, user_db: SQLAlchemyUserDatabase, secret: str):
        super().__init__(user_db)
        self.reset_password_token_secret = secret
        self.verification_token_secret = secret


async def get_user_manager(
        user_db: SQLAlchemyUserDatabase = Depends(get_user_db),
        settings: Settings = Depends(get_settings),
):
    yield UserManager(user_db, settings.auth_secret)


def create_first_admin(settings: Settings, session: Session, logger) -> None:
    """
    Bootstrap the first admin user at startup from ADMIN_EMAIL and
    ADMIN_PASSWORD_HASH. Does nothing if the variables are unset or if a user
    with that email already exists.
    """
    if not settings.admin_email or not settings.admin_password_hash:
        return

    existing = session.exec(select(User).where(User.email == settings.admin_email)).first()
    if existing:
        return

    session.add(User(
        email=settings.admin_email,
        first_name="Admin",
        last_name="Admin",
        role=Role.ADMIN,
        hashed_password=settings.admin_password_hash,
    ))
    session.commit()
    logger.info(f"First admin user {settings.admin_email} created")
