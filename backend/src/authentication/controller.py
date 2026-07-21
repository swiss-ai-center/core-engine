from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException

from authentication.functions import RoleChecker, auth_backend, fastapi_users, get_current_user
from authentication.models import Role, User, UserNameUpdate, UserRead, UserRoleUpdate
from authentication.service import AuthenticationService
from common.exceptions import NotFoundException

router = APIRouter()

# POST /auth/jwt/login and POST /auth/jwt/logout
router.include_router(fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt")


# --- Authenticated user routes ----------------------------------------------

@router.get(
    "/me",
    summary="Get the current authenticated user",
    responses={
        401: {"detail": "Unauthorized"},
    },
    response_model=UserRead,
)
def me(current_user: User = Depends(get_current_user)):
    return current_user


@router.patch(
    "/me",
    summary="Update the current user's name",
    responses={
        401: {"detail": "Unauthorized"},
        422: {"detail": "Invalid first or last name"},
    },
    response_model=UserRead,
)
async def update_me(
        update: UserNameUpdate,
        current_user: User = Depends(get_current_user),
        authentication_service: AuthenticationService = Depends(),
):
    return await authentication_service.update_user_names(current_user, update)


# --- Administrator-only routes ----------------------------------------------

@router.get(
    "/admin/users",
    summary="List all users",
    responses={
        401: {"detail": "Unauthorized"},
        403: {"detail": "Administrator access required"},
    },
    response_model=list[UserRead],
)
async def list_users(
        _current_admin: User = Depends(RoleChecker([Role.ADMIN])),
        authentication_service: AuthenticationService = Depends(),
):
    return await authentication_service.find_many()


@router.patch(
    "/admin/users/{user_id}/role",
    summary="Change a user's role",
    responses={
        401: {"detail": "Unauthorized"},
        403: {"detail": "Administrator access required"},
        404: {"detail": "User not found"},
    },
    response_model=UserRead,
)
async def update_user_role(
        user_id: UUID,
        update: UserRoleUpdate,
        _current_admin: User = Depends(RoleChecker([Role.ADMIN])),
        authentication_service: AuthenticationService = Depends(),
):
    try:
        return await authentication_service.update_user_role(user_id, update)
    except NotFoundException as error:
        raise HTTPException(status_code=404, detail=str(error))
