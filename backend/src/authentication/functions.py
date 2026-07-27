import uuid

from fastapi import Depends, HTTPException, status
from fastapi_users import FastAPIUsers
from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    JWTStrategy,
)

from authentication.models import Role, User
from authentication.service import get_user_manager
from common.exceptions import ForbiddenException
from config import get_settings

bearer_transport = BearerTransport(tokenUrl="auth/jwt/login")


def get_jwt_strategy() -> JWTStrategy:
    settings = get_settings()
    return JWTStrategy(
        secret=settings.auth_secret,
        lifetime_seconds=settings.auth_token_ttl,
    )


auth_backend = AuthenticationBackend(
    name="jwt",
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)

fastapi_users = FastAPIUsers[User, uuid.UUID](get_user_manager, [auth_backend])

# Resolves the user from the Bearer token (401 if missing/invalid/inactive)
get_current_user = fastapi_users.current_user(active=True)
# Resolves the user when a valid token is present while keeping public routes public.
get_optional_current_user = fastapi_users.current_user(active=True, optional=True)


class RoleChecker:
    """
    Dependency restricting a route to the given roles.

    Usage:
        @router.get("/admin", dependencies=[Depends(RoleChecker([Role.ADMIN]))])
    """

    def __init__(self, allowed_roles: list[Role]):
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        try:
            if current_user.role not in self.allowed_roles:
                raise ForbiddenException()
        except ForbiddenException as e:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
        return current_user
