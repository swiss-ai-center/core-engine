from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import PlainTextResponse
from common.exceptions import NotFoundException, ConflictException, ConstraintException
from execution_units.enums import ExecutionUnitStatus
from authentication.functions import RoleChecker, get_optional_current_user
from authentication.models import Role, User
from services.access import ServiceAccessLevel, accessible_service_levels, can_access_service
from services.service import ServicesService
from common.query_parameters import QueryParameters
from services.models import (
    Service,
    ServiceAccessUpdate,
    ServiceCreate,
    ServiceRead,
    ServicesWithCount,
    ServiceUpdate,
)
from uuid import UUID
from sqlalchemy.exc import CompileError
import textwrap

router = APIRouter()


def require_service_access(service: Service | None, current_user: User | None) -> Service:
    """Hide services that the current audience is not allowed to discover."""

    if not service or not can_access_service(
            service.access_level,
            current_user.role if current_user else None,
    ):
        raise HTTPException(status_code=404, detail="Service Not Found")
    return service


@router.get(
    "/services/{service_id}",
    summary="Get one service",
    responses={
        404: {"detail": "Service Not Found"},
        400: {"detail": "Bad Request"},
        500: {"detail": "Internal Server Error"},
    },
    response_model=ServiceRead,
)
def get_one(
        service_id: UUID,
        current_user: User | None = Depends(get_optional_current_user),
        services_service: ServicesService = Depends()
):
    return require_service_access(services_service.find_one(service_id), current_user)


@router.post(
    "/services/{service_id}/wake-up",
    summary="Wake up a service",
    responses={
        404: {"detail": "Service Not Found"},
        500: {"detail": "Internal Server Error"},
    },
    status_code=204
)
async def wake_up_service(
        service_id: UUID,
        current_user: User | None = Depends(get_optional_current_user),
        services_service: ServicesService = Depends()
):
    service = require_service_access(services_service.find_one(service_id), current_user)

    await services_service.wake_up_service(service)


@router.get(
    "/services/{service_id}/code-snippet",
    summary="Get one code snippet by id to use the service externally",
    responses={
        404: {"detail": "Service Not Found"},
        400: {"detail": "Bad Request"},
        500: {"detail": "Internal Server Error"},
    },
    response_class=PlainTextResponse
)
async def get_code_snippet(
        service_id: UUID,
        current_user: User | None = Depends(get_optional_current_user),
        services_service: ServicesService = Depends()
):
    service = require_service_access(services_service.find_one(service_id), current_user)
    raw_snippet = services_service.generate_code_snippet(service)
    # Format the code snippet
    formatted_snippet = textwrap.dedent(raw_snippet).strip()
    return formatted_snippet


@router.get(
    "/services/slug/{service_slug}",
    summary="Get one service by slug",
    responses={
        404: {"detail": "Service Not Found"},
        400: {"detail": "Bad Request"},
        500: {"detail": "Internal Server Error"},
    },
    response_model=ServiceRead,
)
def get_one_by_slug(
        service_slug: str,
        current_user: User | None = Depends(get_optional_current_user),
        services_service: ServicesService = Depends()
):
    return require_service_access(services_service.find_one_by_slug(service_slug), current_user)


@router.post(
    "/services/slug/{service_slug}/wake-up",
    summary="Wake up a service",
    responses={
        404: {"detail": "Service Not Found"},
        500: {"detail": "Internal Server Error"},
    },
    status_code=204
)
async def wake_up_service_by_slug(
        service_slug: str,
        current_user: User | None = Depends(get_optional_current_user),
        services_service: ServicesService = Depends()
):
    service = require_service_access(services_service.find_one_by_slug(service_slug), current_user)

    await services_service.wake_up_service(service)


@router.get(
    "/services/slug/{service_slug}/code-snippet",
    summary="Get one code snippet by slug to use the service externally",
    responses={
        404: {"detail": "Service Not Found"},
        400: {"detail": "Bad Request"},
        500: {"detail": "Internal Server Error"},
    },
    response_class=PlainTextResponse,
)
async def get_code_snippet_by_slug(
        service_slug: str,
        current_user: User | None = Depends(get_optional_current_user),
        services_service: ServicesService = Depends()
):
    service = require_service_access(services_service.find_one_by_slug(service_slug), current_user)

    raw_snippet = services_service.generate_code_snippet(service)

    # Format the code snippet
    formatted_snippet = textwrap.dedent(raw_snippet).strip()

    return formatted_snippet


@router.get(
    "/services",
    summary="Get many services",
    response_model=ServicesWithCount | List[ServiceRead],
)
def get_many_services(
        with_count: bool = False,
        query_parameters: QueryParameters = Depends(),
        current_user: User | None = Depends(get_optional_current_user),
        services_service: ServicesService = Depends(),
):
    try:
        print(query_parameters.status)
        if query_parameters.search:
            query_parameters.search = query_parameters.search.lower()
        if with_count:
            count, services = services_service.find_many_with_total_count(
                query_parameters.search,
                query_parameters.skip,
                query_parameters.limit,
                query_parameters.order_by,
                query_parameters.order,
                query_parameters.tags,
                query_parameters.ai,
                query_parameters.status,
                accessible_service_levels(current_user.role if current_user else None),
            )
            return ServicesWithCount(count=count, services=services)
        else:
            services = services_service.find_many(
                query_parameters.search,
                query_parameters.skip,
                query_parameters.limit,
                query_parameters.order_by,
                query_parameters.order,
                query_parameters.tags,
                query_parameters.ai,
                query_parameters.status,
                accessible_service_levels(current_user.role if current_user else None),
            )
            return services

    except CompileError as e:
        raise HTTPException(status_code=400, detail=str(e))


# --- Administrator-only service access routes -------------------------------

@router.get(
    "/admin/services",
    summary="List all services for administration",
    response_model=ServicesWithCount,
    responses={
        401: {"detail": "Unauthorized"},
        403: {"detail": "Administrator access required"},
    },
)
def get_admin_services(
        query_parameters: QueryParameters = Depends(),
        _current_admin: User = Depends(RoleChecker([Role.ADMIN])),
        services_service: ServicesService = Depends(),
):
    count, services = services_service.find_many_with_total_count(
        query_parameters.search,
        query_parameters.skip,
        query_parameters.limit,
        query_parameters.order_by,
        query_parameters.order,
        query_parameters.tags,
        query_parameters.ai,
        query_parameters.status,
        list(ServiceAccessLevel),
    )
    return ServicesWithCount(count=count, services=services)


@router.patch(
    "/admin/services/{service_id}/access",
    summary="Change a service access level",
    response_model=ServiceRead,
    responses={
        401: {"detail": "Unauthorized"},
        403: {"detail": "Administrator access required"},
        404: {"detail": "Service Not Found"},
    },
)
def update_service_access(
        service_id: UUID,
        update: ServiceAccessUpdate,
        _current_admin: User = Depends(RoleChecker([Role.ADMIN])),
        services_service: ServicesService = Depends(),
):
    try:
        return services_service.update_access_level(service_id, update)
    except NotFoundException as error:
        raise HTTPException(status_code=404, detail=str(error))


@router.post(
    "/services",
    summary="Create a service",
    response_model=ServiceRead,
    responses={
        409: {"detail": "Service Conflict"},
        500: {"detail": "Internal Server Error"},
    },
)
async def create(
        request: Request,
        service: ServiceCreate,
        services_service: ServicesService = Depends(),
):
    try:
        service_create = Service.model_validate(service)
        service = await services_service.create(service_create, request.app)

        return service
    except ConflictException as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.patch(
    "/services/{service_id}",
    summary="Update a service",
    responses={
        404: {"detail": "Service Not Found"},
        500: {"detail": "Internal Server Error"},
    },
    response_model=ServiceRead,
)
def update(
        request: Request,
        service_id: UUID,
        service_update: ServiceUpdate,
        services_service: ServicesService = Depends(),
):
    try:
        service = services_service.update(service_id, service_update)
        if service.status == ExecutionUnitStatus.AVAILABLE:
            services_service.enable_service(request.app, service)
        else:
            services_service.disable_service(request.app, service)
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))

    return service


@router.delete(
    "/services/{service_id}",
    summary="Delete a service",
    description="Delete a service and all its tasks",
    responses={
        204: {"detail": "Service Removed"},
        404: {"detail": "Service Not Found"},
        500: {"detail": "Internal Server Error"},
    },
    status_code=204
)
def delete(
        request: Request,
        service_id: UUID,
        services_service: ServicesService = Depends(),
):
    try:
        services_service.delete(service_id, request.app)
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ConstraintException as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.post(
    "/services/{service_slug}/ping",
    summary="Services health check endpoint",
    responses={
        200: {"detail": "Service is healthy"},
        404: {"detail": "Service Not Found"},
        503: {"detail": "Service is unhealthy"},
    },
    status_code=200
)
def heartbeat_endpoint(
        service_slug: str,
        services_service: ServicesService = Depends(),
):
    service = services_service.find_one_by_slug(service_slug)
    if not service:
        raise HTTPException(status_code=404, detail="Service Not Found")

    now = datetime.now()
    services_service.update(service.id, ServiceUpdate(latest_ping=now))
