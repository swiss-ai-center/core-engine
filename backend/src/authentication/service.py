from uuid import UUID

from fastapi import Depends
from fastapi_users import BaseUserManager, UUIDIDMixin
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import Session, select

from authentication.models import Role, User, UserNameUpdate, UserRoleUpdate
from common.exceptions import NotFoundException
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


class AuthenticationService:
    def __init__(self, session: AsyncSession = Depends(get_async_session)):
        self.session = session

    async def update_user_names(self, user: User, update: UserNameUpdate) -> User:
        user.first_name = update.first_name
        user.last_name = update.last_name
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user

    async def find_many(self) -> list[User]:
        result = await self.session.execute(select(User).order_by(User.email))
        return list(result.scalars().all())

    async def update_user_role(self, user_id: UUID, update: UserRoleUpdate) -> User:
        user = await self.session.get(User, user_id)
        if not user:
            raise NotFoundException("User Not Found")

        user.role = update.role
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user


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
