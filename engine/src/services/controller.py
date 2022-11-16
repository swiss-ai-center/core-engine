from fastapi import APIRouter, Depends

from .models import ServiceModel
from .service import ServicesService
from logger import Logger

router = APIRouter()


@router.get("/services", summary="Get all services", response_model=ServiceModel)
async def get_services(services_service: ServicesService = Depends()):
    pipelines = await services_service.get_services()
    return pipelines


@router.delete("/services/{service_name}", summary="Remove a service")
async def delete_service(service_name: str, services_service: ServicesService = Depends()):
    await services_service.delete(service_name)


@router.get("/services/{service_name}", summary="Get a service description", response_model=ServiceModel)
async def getPipeline(service_name: str, services_service: ServicesService = Depends()):
    service = await services_service.find_one(service_name)
    return service


@router.post("/services", summary="Create a new service")
async def create(service: ServiceModel, services_service: ServicesService = Depends(), logger: Logger = Depends()):
    service_name = service.api.route
    try:
        services_service.create(service_name, service)
    # TODO: create pipeline_from_service
    except Exception as e:
        logger.error(e)
        return {"message": "Service already exists"}
