import types
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient
from fastapi_users.password import PasswordHelper
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlmodel import Session, SQLModel, create_engine

from authentication.controller import router as auth_router
from authentication.functions import RoleChecker
from authentication.models import Role, User, UserNameUpdate, UserRoleUpdate
from authentication.service import AuthenticationService, create_first_admin
from common.exceptions import NotFoundException
from database import get_async_session
from main import app as main_app

USER_EMAIL = "user@example.com"
USER_PASSWORD = "userpass123"
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "adminpass123"


@pytest.fixture(name="async_engine")
def async_engine_fixture(tmp_path):
    """
    A file-backed SQLite database seeded with a user and an admin.

    A file (not :memory:) is used so the sync engine that seeds the rows and
    the async engine that fastapi-users uses at request time share the same
    database without fighting over event loops.
    """
    db_file = tmp_path / "auth-test.db"
    sync_engine = create_engine(f"sqlite:///{db_file}")
    SQLModel.metadata.create_all(sync_engine)

    helper = PasswordHelper()
    with Session(sync_engine) as session:
        session.add(User(
            email=USER_EMAIL, first_name="Reg", last_name="User",
            role=Role.USER, hashed_password=helper.hash(USER_PASSWORD),
        ))
        session.add(User(
            email=ADMIN_EMAIL, first_name="Ad", last_name="Min",
            role=Role.ADMIN, hashed_password=helper.hash(ADMIN_PASSWORD),
        ))
        session.commit()

    async_engine = create_async_engine(f"sqlite+aiosqlite:///{db_file}")
    yield async_engine


@pytest.fixture(name="client")
def client_fixture(async_engine):
    """
    A client on a minimal app wiring the real auth router plus two routes
    guarded by RoleChecker, all backed by the seeded database.
    """
    async def get_async_session_override():
        async with AsyncSession(async_engine, expire_on_commit=False) as session:
            yield session

    app = FastAPI()
    app.include_router(auth_router)

    @app.get("/only-admin", dependencies=[Depends(RoleChecker([Role.ADMIN]))])
    def only_admin():
        return {"ok": True}

    @app.get("/any-user")
    def any_user(user: User = Depends(RoleChecker([Role.USER, Role.ADMIN]))):
        return {"email": user.email}

    app.dependency_overrides[get_async_session] = get_async_session_override

    yield TestClient(app)

    app.dependency_overrides.clear()


def _login(client: TestClient, email: str, password: str):
    return client.post("/auth/jwt/login", data={"username": email, "password": password})


def _token(client: TestClient, email: str, password: str) -> str:
    return _login(client, email, password).json()["access_token"]


# --- Login -------------------------------------------------------------------

def test_login_success_returns_token(client: TestClient):
    response = _login(client, USER_EMAIL, USER_PASSWORD)
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


def test_login_wrong_password_is_rejected(client: TestClient):
    response = _login(client, USER_EMAIL, "not-my-password")
    assert response.status_code == 400


def test_login_unknown_user_is_rejected(client: TestClient):
    response = _login(client, "ghost@example.com", "whatever123")
    assert response.status_code == 400


# --- /me ---------------------------------------------------------------------

def test_me_without_token_is_unauthorized(client: TestClient):
    assert client.get("/me").status_code == 401


def test_me_with_invalid_token_is_unauthorized(client: TestClient):
    response = client.get("/me", headers={"Authorization": "Bearer not-a-real-token"})
    assert response.status_code == 401


def test_me_with_token_returns_user_without_password(client: TestClient):
    token = _token(client, USER_EMAIL, USER_PASSWORD)
    response = client.get("/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    body = response.json()
    assert body["email"] == USER_EMAIL
    assert body["role"] == Role.USER.value
    # The password hash must never be exposed through the API.
    assert "hashed_password" not in body
    assert "password" not in body


def test_update_me_changes_first_and_last_name(client: TestClient):
    token = _token(client, USER_EMAIL, USER_PASSWORD)
    headers = {"Authorization": f"Bearer {token}"}

    response = client.patch(
        "/me",
        headers=headers,
        json={"first_name": "Updated", "last_name": "Person"},
    )

    assert response.status_code == 200
    assert response.json()["first_name"] == "Updated"
    assert response.json()["last_name"] == "Person"
    assert client.get("/me", headers=headers).json()["first_name"] == "Updated"


def test_update_me_strips_names_and_rejects_blank_values(client: TestClient):
    token = _token(client, USER_EMAIL, USER_PASSWORD)
    headers = {"Authorization": f"Bearer {token}"}

    response = client.patch(
        "/me",
        headers=headers,
        json={"first_name": "  Trimmed  ", "last_name": "  Name  "},
    )
    assert response.status_code == 200
    assert response.json()["first_name"] == "Trimmed"
    assert response.json()["last_name"] == "Name"

    blank_response = client.patch(
        "/me",
        headers=headers,
        json={"first_name": "   ", "last_name": "Name"},
    )
    assert blank_response.status_code == 422


def test_update_me_without_token_is_unauthorized(client: TestClient):
    response = client.patch("/me", json={"first_name": "New", "last_name": "Name"})
    assert response.status_code == 401


# --- User administration ----------------------------------------------------

def test_admin_can_list_all_users_without_passwords(client: TestClient):
    token = _token(client, ADMIN_EMAIL, ADMIN_PASSWORD)
    response = client.get("/admin/users", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    users = response.json()
    assert [user["email"] for user in users] == [ADMIN_EMAIL, USER_EMAIL]
    assert all("hashed_password" not in user for user in users)
    assert all("password" not in user for user in users)


def test_regular_user_cannot_list_users(client: TestClient):
    token = _token(client, USER_EMAIL, USER_PASSWORD)
    response = client.get("/admin/users", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403


def test_unauthenticated_user_cannot_list_users(client: TestClient):
    response = client.get("/admin/users")
    assert response.status_code == 401


def test_admin_can_promote_and_downgrade_user(client: TestClient):
    admin_token = _token(client, ADMIN_EMAIL, ADMIN_PASSWORD)
    headers = {"Authorization": f"Bearer {admin_token}"}
    users = client.get("/admin/users", headers=headers).json()
    user_id = next(user["id"] for user in users if user["email"] == USER_EMAIL)

    promoted = client.patch(
        f"/admin/users/{user_id}/role",
        headers=headers,
        json={"role": Role.ADMIN.value},
    )
    assert promoted.status_code == 200
    assert promoted.json()["role"] == Role.ADMIN.value

    downgraded = client.patch(
        f"/admin/users/{user_id}/role",
        headers=headers,
        json={"role": Role.USER.value},
    )
    assert downgraded.status_code == 200
    assert downgraded.json()["role"] == Role.USER.value


def test_regular_user_cannot_change_roles(client: TestClient):
    token = _token(client, USER_EMAIL, USER_PASSWORD)
    response = client.patch(
        f"/admin/users/{uuid4()}/role",
        headers={"Authorization": f"Bearer {token}"},
        json={"role": Role.ADMIN.value},
    )
    assert response.status_code == 403


def test_unauthenticated_user_cannot_change_roles(client: TestClient):
    response = client.patch(
        f"/admin/users/{uuid4()}/role",
        json={"role": Role.ADMIN.value},
    )
    assert response.status_code == 401


def test_role_update_returns_not_found_for_unknown_user(client: TestClient):
    token = _token(client, ADMIN_EMAIL, ADMIN_PASSWORD)
    response = client.patch(
        f"/admin/users/{uuid4()}/role",
        headers={"Authorization": f"Bearer {token}"},
        json={"role": Role.USER.value},
    )
    assert response.status_code == 404


# --- RoleChecker -------------------------------------------------------------

def test_admin_route_allows_admin(client: TestClient):
    token = _token(client, ADMIN_EMAIL, ADMIN_PASSWORD)
    response = client.get("/only-admin", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json() == {"ok": True}


def test_admin_route_forbids_regular_user(client: TestClient):
    token = _token(client, USER_EMAIL, USER_PASSWORD)
    response = client.get("/only-admin", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403


def test_admin_route_without_token_is_unauthorized(client: TestClient):
    assert client.get("/only-admin").status_code == 401


def test_shared_route_allows_regular_user(client: TestClient):
    token = _token(client, USER_EMAIL, USER_PASSWORD)
    response = client.get("/any-user", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json() == {"email": USER_EMAIL}


# --- AuthenticationService --------------------------------------------------

@pytest.mark.asyncio
async def test_authentication_service_updates_user_names():
    session = MagicMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    service = AuthenticationService(session)
    user = User(
        email=USER_EMAIL,
        first_name="Old",
        last_name="Name",
        role=Role.USER,
        hashed_password="hash",
    )
    update = UserNameUpdate(first_name="New", last_name="Person")

    result = await service.update_user_names(user, update)

    assert result is user
    assert user.first_name == "New"
    assert user.last_name == "Person"
    session.add.assert_called_once_with(user)
    session.commit.assert_awaited_once()
    session.refresh.assert_awaited_once_with(user)


@pytest.mark.asyncio
async def test_authentication_service_lists_users():
    users = [MagicMock(spec=User), MagicMock(spec=User)]
    result = MagicMock()
    result.scalars.return_value.all.return_value = users
    session = MagicMock()
    session.execute = AsyncMock(return_value=result)
    service = AuthenticationService(session)

    assert await service.find_many() == users
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_authentication_service_updates_user_role():
    session = MagicMock()
    session.get = AsyncMock()
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    user = User(
        email=USER_EMAIL,
        first_name="Reg",
        last_name="User",
        role=Role.USER,
        hashed_password="hash",
    )
    session.get.return_value = user
    service = AuthenticationService(session)

    result = await service.update_user_role(user.id, UserRoleUpdate(role=Role.ADMIN))

    assert result is user
    assert user.role == Role.ADMIN
    session.add.assert_called_once_with(user)
    session.commit.assert_awaited_once()
    session.refresh.assert_awaited_once_with(user)


@pytest.mark.asyncio
async def test_authentication_service_role_update_rejects_unknown_user():
    session = MagicMock()
    session.get = AsyncMock(return_value=None)
    service = AuthenticationService(session)

    with pytest.raises(NotFoundException, match="User Not Found"):
        await service.update_user_role(uuid4(), UserRoleUpdate(role=Role.ADMIN))


# --- First-admin bootstrap ---------------------------------------------------

def test_create_first_admin_creates_admin_when_configured():
    engine = create_engine("sqlite://")
    SQLModel.metadata.create_all(engine)
    settings = types.SimpleNamespace(
        admin_email="boot@example.com",
        admin_password_hash=PasswordHelper().hash("bootpass"),
    )
    logger = types.SimpleNamespace(info=lambda *_: None)

    with Session(engine) as session:
        create_first_admin(settings, session, logger)
        # Second call must be idempotent: no duplicate, no error.
        create_first_admin(settings, session, logger)
        users = session.query(User).filter(User.email == "boot@example.com").all()

    assert len(users) == 1
    assert users[0].role == Role.ADMIN


def test_create_first_admin_skipped_when_unconfigured():
    engine = create_engine("sqlite://")
    SQLModel.metadata.create_all(engine)
    settings = types.SimpleNamespace(admin_email=None, admin_password_hash=None)
    logger = types.SimpleNamespace(info=lambda *_: None)

    with Session(engine) as session:
        create_first_admin(settings, session, logger)
        assert session.query(User).count() == 0


# --- Real app wiring ---------------------------------------------------------

def test_auth_routes_are_registered_on_the_app():
    paths = {route.path for route in main_app.routes}
    assert "/me" in paths
    assert "/auth/jwt/login" in paths
    assert "/admin/users" in paths
    assert "/admin/users/{user_id}/role" in paths
