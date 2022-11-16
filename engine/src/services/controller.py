from fastapi import APIRouter, Depends

from .models.service import ServiceModel
from .schemas.service import ServiceSchema
from .service import ServicesService
from logger import Logger

router = APIRouter()


@router.get("/services", summary="Get all services", response_model=ServiceModel)
async def get_services(services_service: ServicesService = Depends()):
    pipelines = await services_service.get_services()
    return pipelines


@router.delete("/services/{serviceName}", summary="Remove a service")
async def delete_service(service_name: str, services_service: ServicesService = Depends()):
    await services_service.delete(service_name)


@router.get("/services/{serviceName}", summary="Get the service description", response_model=ServiceSchema)
async def getPipeline(service_name: str, services_service: ServicesService = Depends()):
    service = await services_service.find_one(service_name)
    return service


@router.post("/services", summary="Create a new service")
async def create(service: ServiceSchema, services_service: ServicesService = Depends(), logger: Logger = Depends()):
    service_name = service.api.route
    try:
        services_service.create(service_name, service)
    # TODO: create pipeline_from_service
    except Exception as e:
        logger.error(e)
        return {"message": "Service already exists"}
