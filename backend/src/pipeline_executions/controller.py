from typing import List
from fastapi import APIRouter, Depends, HTTPException
from common.exceptions import NotFoundException, UnprocessableEntityException
from pipeline_executions.service import PipelineExecutionsService
from common.query_parameters import QueryParameters
from pipeline_executions.models import PipelineExecution, PipelineExecutionRead, PipelineExecutionUpdate, \
    PipelineExecutionCreate, PipelineExecutionReadWithPipelineAndTasks
from uuid import UUID

router = APIRouter()


@router.get(
    "/pipeline-executions/{pipeline_execution_id}",
    summary="Get one pipeline execution",
    responses={
        404: {"detail": "Pipeline Execution Not Found"},
        400: {"detail": "Bad Request"},
        500: {"detail": "Internal Server Error"},
    },
    response_model=PipelineExecutionReadWithPipelineAndTasks,
)
def get_one(
        pipeline_execution_id: UUID,
        pipeline_executions_service: PipelineExecutionsService = Depends()
):
    pipeline_execution = pipeline_executions_service.find_one(pipeline_execution_id)
    if not pipeline_execution:
        raise HTTPException(status_code=404, detail="Pipeline Execution Not Found")

    return pipeline_execution


@router.get(
    "/pipeline-executions",
    summary="Get many pipeline executions",
    response_model=List[PipelineExecutionReadWithPipelineAndTasks],
)
def get_many_pipelines(
        query_parameters: QueryParameters = Depends(),
        pipeline_executions_service: PipelineExecutionsService = Depends(),
):
    pipeline_executions = pipeline_executions_service.find_many(
        query_parameters.skip,
        query_parameters.limit,
        query_parameters.order_by,
        query_parameters.order,
    )

    return pipeline_executions


@router.post(
    "/pipeline-executions",
    summary="Create a pipeline execution",
    response_model=PipelineExecutionRead,
)
def create(
        pipeline: PipelineExecutionCreate,
        pipeline_executions_service: PipelineExecutionsService = Depends(),
):
    try:
        pipeline_execution_create = PipelineExecution.model_validate(pipeline)
        pipeline_execution = pipeline_executions_service.create(pipeline_execution_create)
    except UnprocessableEntityException as e:
        raise HTTPException(status_code=422, detail=str(e))

    return pipeline_execution


@router.patch(
    "/pipeline-executions/{pipeline_execution_id}",
    summary="Update a pipeline execution",
    responses={
        404: {"detail": "Pipeline Execution Not Found"},
        500: {"detail": "Internal Server Error"},
    },
    response_model=PipelineExecutionRead,
)
def update(
        pipeline_id: UUID,
        pipeline_execution_update: PipelineExecutionUpdate,
        pipeline_executions_service: PipelineExecutionsService = Depends(),
):
    try:
        pipeline_execution = pipeline_executions_service.update(pipeline_id, pipeline_execution_update)
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except UnprocessableEntityException as e:
        raise HTTPException(status_code=422, detail=str(e))

    return pipeline_execution


@router.delete(
    "/pipeline-executions/{pipeline_execution_id}",
    summary="Delete a pipeline execution",
    responses={
        204: {"detail": "Pipeline Execution Removed"},
        404: {"detail": "Pipeline Execution Not Found"},
        500: {"detail": "Internal Server Error"},
    },
    status_code=204
)
def delete(
        pipeline_execution_id: UUID,
        pipeline_executions_service: PipelineExecutionsService = Depends(),
):
    try:
        pipeline_executions_service.delete(pipeline_execution_id)
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
