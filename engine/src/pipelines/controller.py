from fastapi import APIRouter, Depends
from logger import Logger
from .service import PipelinesService
from .models import PipelineModel

router = APIRouter()


@router.get("/pipelines")
async def get_all():
    return [{"pipeline1": "pipeline2"}]


@router.get("/pipelines", summary="Get all pipelines", response_model=PipelineModel)
async def get_services(pipelines_service: PipelinesService = Depends()):
    pipelines = await pipelines_service.get_pipelines()
    return pipelines


@router.delete("/pipelines/{pipeline_name}", summary="Remove a pipeline")
async def delete(pipeline_name: str, pipelines_service: PipelinesService = Depends()):
    await pipelines_service.delete(pipeline_name)


@router.get("/pipelines/{pipeline_name}", summary="Get a pipeline description", response_model=PipelineModel)
async def find_one(pipeline_name: str, pipelines_service: PipelinesService = Depends()):
    service = await pipelines_service.find_one(pipeline_name)
    return service


# TODO: implement pipeline creation
@router.post("/pipelines", summary="Create a new pipeline")
async def create(pipeline: PipelineModel, pipelines_service: PipelinesService = Depends(), logger: Logger = Depends()):
    pass
