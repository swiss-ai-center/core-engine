from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from fastapi_users.password import PasswordHelper
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlmodel import Session, SQLModel, create_engine

from authentication.controller import router as authentication_router
from authentication.models import Role, User
from database import get_async_session, get_session
from main import app as _main_app  # Import models in the application's established order.
from pipeline_steps.models import PipelineStep
from pipelines.controller import router as pipelines_router
from pipelines.models import Pipeline
from pipelines.service import PipelinesService
from services.access import ServiceAccessLevel
from services.controller import router as services_router
from services.models import Service
from services.service import ServicesService

USER_EMAIL = "service-user@example.com"
USER_PASSWORD = "service-user-password"
ADMIN_EMAIL = "service-admin@example.com"
ADMIN_PASSWORD = "service-admin-password"


@pytest.fixture(scope="session", autouse=True, name="minio")
def no_minio_needed():
    """These access tests do not perform storage operations."""

    yield None


@pytest.fixture(name="client_and_services")
def client_and_services_fixture(tmp_path):
    database_file = tmp_path / "service-access.db"
    sync_engine = create_engine(f"sqlite:///{database_file}")
    SQLModel.metadata.create_all(sync_engine)
    password_helper = PasswordHelper()

    session = Session(sync_engine)
    session.add(User(
        email=USER_EMAIL,
        first_name="Service",
        last_name="User",
        role=Role.USER,
        hashed_password=password_helper.hash(USER_PASSWORD),
    ))
    session.add(User(
        email=ADMIN_EMAIL,
        first_name="Service",
        last_name="Admin",
        role=Role.ADMIN,
        hashed_password=password_helper.hash(ADMIN_PASSWORD),
    ))

    services = []
    for access_level in ServiceAccessLevel:
        service = Service(
            name=f"{access_level.value.title()} service",
            slug=f"{access_level.value}-service",
            summary="Access test service",
            description="Access test service",
            data_in_fields=[],
            data_out_fields=[],
            url="http://service.local",
            access_level=access_level,
        )
        session.add(service)
        services.append(service)
    session.flush()

    pipelines = []
    for service in services:
        pipeline = Pipeline(
            name=f"{service.access_level.value.title()} pipeline",
            slug=f"{service.access_level.value}-pipeline",
            summary="Pipeline access test",
            description="Pipeline access test",
            data_in_fields=[],
            data_out_fields=[],
        )
        session.add(pipeline)
        session.flush()
        session.add(PipelineStep(
            identifier=f"{service.access_level.value}-step",
            needs=[],
            inputs=[],
            pipeline_id=pipeline.id,
            service_id=service.id,
        ))
        pipelines.append(pipeline)
    session.commit()
    for model in [*services, *pipelines]:
        session.refresh(model)

    async_engine = create_async_engine(f"sqlite+aiosqlite:///{database_file}")

    async def get_async_session_override():
        async with AsyncSession(async_engine, expire_on_commit=False) as async_session:
            yield async_session

    def get_session_override():
        yield session

    services_service = ServicesService(
        logger=MagicMock(),
        storage_service=MagicMock(),
        tasks_service=MagicMock(),
        settings=MagicMock(),
        session=session,
        http_client=MagicMock(),
    )
    pipelines_service = PipelinesService(
        logger=MagicMock(),
        storage_service=MagicMock(),
        session=session,
        pipeline_executions_service=MagicMock(),
        tasks_service=MagicMock(),
        settings=MagicMock(),
        services_service=services_service,
        http_client=MagicMock(),
    )

    app = FastAPI()
    app.include_router(authentication_router)
    app.include_router(services_router)
    app.include_router(pipelines_router)
    app.dependency_overrides[get_async_session] = get_async_session_override
    app.dependency_overrides[get_session] = get_session_override
    app.dependency_overrides[ServicesService] = lambda: services_service
    app.dependency_overrides[PipelinesService] = lambda: pipelines_service

    # Register one protected generated execution route to verify enforcement at use time.
    admin_service = next(service for service in services if service.access_level == ServiceAccessLevel.ADMIN)
    services_service.enable_service(app, admin_service)

    yield TestClient(app), services, pipelines

    session.close()
    app.dependency_overrides.clear()


def token(client: TestClient, email: str, password: str) -> str:
    response = client.post("/auth/jwt/login", data={"username": email, "password": password})
    assert response.status_code == 200
    return response.json()["access_token"]


def authorization(token_value: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token_value}"}


def service_slugs(response) -> set[str]:
    return {service["slug"] for service in response.json()}


def test_service_access_defaults_to_public():
    service = Service(
        name="Default",
        slug="default",
        summary="Default access",
        data_in_fields=[],
        data_out_fields=[],
        url="http://service.local",
    )
    assert service.access_level == ServiceAccessLevel.PUBLIC


def test_catalog_visibility_matches_current_role(client_and_services):
    client, _, _ = client_and_services

    assert service_slugs(client.get("/services")) == {"public-service"}

    user_token = token(client, USER_EMAIL, USER_PASSWORD)
    assert service_slugs(client.get("/services", headers=authorization(user_token))) == {
        "public-service",
        "user-service",
    }

    admin_token = token(client, ADMIN_EMAIL, ADMIN_PASSWORD)
    assert service_slugs(client.get("/services", headers=authorization(admin_token))) == {
        "public-service",
        "user-service",
        "admin-service",
    }


def test_restricted_service_is_hidden_from_direct_reads(client_and_services):
    client, services, _ = client_and_services
    user_service = next(service for service in services if service.access_level == ServiceAccessLevel.USER)

    assert client.get(f"/services/{user_service.id}").status_code == 404

    user_token = token(client, USER_EMAIL, USER_PASSWORD)
    assert client.get(
        f"/services/{user_service.id}",
        headers=authorization(user_token),
    ).status_code == 200


def test_generated_execution_route_enforces_service_access(client_and_services):
    client, _, _ = client_and_services
    assert client.post("/admin-service").status_code == 403

    user_token = token(client, USER_EMAIL, USER_PASSWORD)
    assert client.post("/admin-service", headers=authorization(user_token)).status_code == 403


def test_only_admin_can_list_every_service(client_and_services):
    client, _, _ = client_and_services
    assert client.get("/admin/services").status_code == 401

    user_token = token(client, USER_EMAIL, USER_PASSWORD)
    assert client.get("/admin/services", headers=authorization(user_token)).status_code == 403

    admin_token = token(client, ADMIN_EMAIL, ADMIN_PASSWORD)
    response = client.get("/admin/services", headers=authorization(admin_token))
    assert response.status_code == 200
    assert response.json()["count"] == 4
    assert {service["access_level"] for service in response.json()["services"]} == {
        access_level.value for access_level in ServiceAccessLevel
    }


def test_only_admin_can_change_service_access(client_and_services):
    client, services, _ = client_and_services
    public_service = next(
        service for service in services if service.access_level == ServiceAccessLevel.PUBLIC
    )
    path = f"/admin/services/{public_service.id}/access"
    payload = {"access_level": ServiceAccessLevel.DISABLED.value}

    assert client.patch(path, json=payload).status_code == 401

    user_token = token(client, USER_EMAIL, USER_PASSWORD)
    assert client.patch(path, headers=authorization(user_token), json=payload).status_code == 403

    admin_token = token(client, ADMIN_EMAIL, ADMIN_PASSWORD)
    response = client.patch(path, headers=authorization(admin_token), json=payload)
    assert response.status_code == 200
    assert response.json()["access_level"] == ServiceAccessLevel.DISABLED.value
    assert client.get(f"/services/{public_service.id}", headers=authorization(admin_token)).status_code == 404


def pipeline_slugs(response) -> set[str]:
    return {pipeline["slug"] for pipeline in response.json()}


def test_pipeline_catalog_hides_pipelines_with_inaccessible_services(client_and_services):
    client, _, _ = client_and_services

    assert pipeline_slugs(client.get("/pipelines")) == {"public-pipeline"}

    user_token = token(client, USER_EMAIL, USER_PASSWORD)
    assert pipeline_slugs(client.get("/pipelines", headers=authorization(user_token))) == {
        "public-pipeline",
        "user-pipeline",
    }

    admin_token = token(client, ADMIN_EMAIL, ADMIN_PASSWORD)
    assert pipeline_slugs(client.get("/pipelines", headers=authorization(admin_token))) == {
        "public-pipeline",
        "user-pipeline",
        "admin-pipeline",
    }


def test_inaccessible_pipeline_is_hidden_from_direct_reads(client_and_services):
    client, _, pipelines = client_and_services
    user_pipeline = next(pipeline for pipeline in pipelines if pipeline.slug == "user-pipeline")

    assert client.get(f"/pipelines/{user_pipeline.id}").status_code == 404

    user_token = token(client, USER_EMAIL, USER_PASSWORD)
    assert client.get(
        f"/pipelines/{user_pipeline.id}",
        headers=authorization(user_token),
    ).status_code == 200


def test_admin_pipeline_list_remains_complete(client_and_services):
    client, _, _ = client_and_services
    assert client.get("/admin/pipelines").status_code == 401

    user_token = token(client, USER_EMAIL, USER_PASSWORD)
    assert client.get("/admin/pipelines", headers=authorization(user_token)).status_code == 403

    admin_token = token(client, ADMIN_EMAIL, ADMIN_PASSWORD)
    response = client.get("/admin/pipelines", headers=authorization(admin_token))
    assert response.status_code == 200
    assert response.json()["count"] == 4
