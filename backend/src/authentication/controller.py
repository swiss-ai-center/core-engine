from fastapi import APIRouter, Depends

from authentication.functions import auth_backend, fastapi_users, get_current_user
from authentication.models import User, UserRead

router = APIRouter()

# POST /auth/jwt/login and POST /auth/jwt/logout
router.include_router(fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt")


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
