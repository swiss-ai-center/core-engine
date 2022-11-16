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


@router.post("/services", summary="Create a new service")
async def create(service: ServiceSchema, services_service: ServicesService = Depends(), logger: Logger = Depends()):
	service_name = service.api.route
	try:
		services_service.create(service_name, service)
		# TODO: create pipeline_from_service
	except Exception as e:
		logger.error(e)
		return {"message": "Service already exists"}