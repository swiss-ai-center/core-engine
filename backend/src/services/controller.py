from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request
from common.exceptions import NotFoundException, ConflictException, ConstraintException
from execution_units.enums import ExecutionUnitStatus
from services.service import ServicesService
from common.query_parameters import QueryParameters
from services.models import ServiceRead, ServiceUpdate, ServiceCreate, Service, ServicesWithCount
from uuid import UUID
from sqlalchemy.exc import CompileError

router = APIRouter()


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
        services_service: ServicesService = Depends()
):
    service = services_service.find_one(service_id)
    if not service:
        raise HTTPException(status_code=404, detail="Service Not Found")

    return service


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
        services_service: ServicesService = Depends()
):
    service = services_service.find_one_by_slug(service_slug)
    if not service:
        raise HTTPException(status_code=404, detail="Service Not Found")

    return service


@router.get(
    "/services",
    summary="Get many services",
    response_model=ServicesWithCount | List[ServiceRead],
)
def get_many_services(
        with_count: bool = False,
        query_parameters: QueryParameters = Depends(),
        services_service: ServicesService = Depends(),
):
    try:
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
                query_parameters.status
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
                query_parameters.status
            )
            return services

    except CompileError as e:
        raise HTTPException(status_code=400, detail=str(e))


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
