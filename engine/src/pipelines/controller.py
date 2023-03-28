from typing import List
from fastapi import APIRouter, Depends, HTTPException
from common.exceptions import NotFoundException
from pipelines.service import PipelinesService
from common.query_parameters import SkipAndLimit
from pipelines.models import PipelineRead, PipelineUpdate, PipelineCreate, Pipeline, \
    PipelineReadWithPipelineElementsAndTasks
from uuid import UUID
from pipeline_elements.service import PipelineElementsService

router = APIRouter()


@router.get(
    "/pipelines/{pipeline_id}",
    summary="Get one pipeline",
    responses={
        404: {"detail": "Pipeline Not Found"},
        400: {"detail": "Bad Request"},
        500: {"detail": "Internal Server Error"},
    },
    response_model=PipelineReadWithPipelineElementsAndTasks,
)
def get_one(
        pipeline_id: UUID,
        pipelines_service: PipelinesService = Depends()
):
    pipeline = pipelines_service.find_one(pipeline_id)
    if not pipeline:
        raise HTTPException(status_code=404, detail="Pipeline Not Found")

    return pipeline


@router.get(
    "/pipelines",
    summary="Get many pipelines",
    response_model=List[PipelineRead],
)
def get_many_pipelines(
        skip_and_limit: SkipAndLimit = Depends(),
        pipelines_service: PipelinesService = Depends(),
):
    pipelines = pipelines_service.find_many(skip_and_limit.skip, skip_and_limit.limit)

    return pipelines


@router.post(
    "/pipelines",
    summary="Create a pipeline",
    response_model=PipelineReadWithPipelineElementsAndTasks,
)
def create(
    pipeline: PipelineCreate,
    pipelines_service: PipelinesService = Depends(),
    pipeline_elements_service: PipelineElementsService = Depends(),
):
    pipeline_elements = []
    for pipeline_element_id in pipeline.pipeline_elements:
        pipeline_elements.append(pipeline_elements_service.find_one(pipeline_element_id))
    pipeline_create = Pipeline.from_orm(pipeline)
    pipeline_create.pipeline_elements = pipeline_elements
    pipeline = pipelines_service.create(pipeline_create)

    return pipeline


@router.patch(
    "/pipelines/{pipeline_id}",
    summary="Update a pipeline",
    responses={
        404: {"detail": "Pipeline Not Found"},
        500: {"detail": "Internal Server Error"},
    },
    response_model=PipelineReadWithPipelineElementsAndTasks,
)
def update(
        pipeline_id: UUID,
        pipeline_update: PipelineUpdate,
        pipelines_service: PipelinesService = Depends(),
):
    try:
        pipeline = pipelines_service.update(pipeline_id, pipeline_update)
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))

    return pipeline


@router.delete(
    "/pipelines/{pipeline_id}",
    summary="Delete a pipeline",
    responses={
        204: {"detail": "Pipeline Removed"},
        404: {"detail": "Pipeline Not Found"},
        500: {"detail": "Internal Server Error"},
    },
    status_code=204
)
def delete(
        pipeline_id: UUID,
        pipelines_service: PipelinesService = Depends(),
):
    try:
        pipelines_service.delete(pipeline_id)
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post(
    "/pipeline/check",
    summary="Check if a pipeline is valid",
    responses={
        400: {"detail": "Bad Request"},
        500: {"detail": "Internal Server Error"},
    }
)
def check(
        pipeline: PipelineCreate,
        pipelines_service: PipelinesService = Depends(),
):
    try:
        if pipelines_service.check_pipeline_consistency(pipeline):
            return {"valid": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
