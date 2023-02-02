from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request
from common.exceptions import NotFoundException, ConflictException
from .service import ServicesService
from common.query_parameters import SkipAndLimit
from .models import ServiceRead, ServiceUpdate, ServiceCreate, Service, ServiceReadWithTasks, ServiceStatus
from uuid import UUID

router = APIRouter()


@router.get(
    "/services/{service_id}",
    summary="Get one service",
    responses={
        404: {"detail": "Service Not Found"},
        400: {"detail": "Bad Request"},
        500: {"detail": "Internal Server Error"},
    },
    response_model=ServiceReadWithTasks,
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
    "/services",
    summary="Get many services",
    response_model=List[ServiceRead],
)
def get_many_services(
        skip_and_limit: SkipAndLimit = Depends(),
        services_service: ServicesService = Depends(),
):
    services = services_service.find_many(skip_and_limit.skip, skip_and_limit.limit)

    return services


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
        service_create = Service.from_orm(service)
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
        if service.status == ServiceStatus.AVAILABLE:
            services_service.enable_service(request.app, service)
        else:
            services_service.disable_service(request.app, service)
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))

    return service


@router.delete(
    "/services/{service_id}",
    summary="Delete a service",
    responses={
        204: {"detail": "Service Removed"},
        404: {"detail": "Service Not Found"},
        500: {"detail": "Internal Server Error"},
    },
    status_code=204
)
def delete(
        service_id: UUID,
        services_service: ServicesService = Depends(),
):
    try:
        services_service.delete(service_id)
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
