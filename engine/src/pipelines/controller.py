from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request
from common.exceptions import NotFoundException, InconsistentPipelineException
from pipelines.service import PipelinesService
from common.query_parameters import SkipLimitOrderByAndOrder
from pipelines.models import PipelineRead, PipelineUpdate, PipelineCreate, Pipeline, \
    PipelineReadWithPipelineStepsAndTasks
from pipeline_steps.models import PipelineStep
from uuid import UUID, uuid4
from sqlalchemy.exc import CompileError

router = APIRouter()


@router.get(
    "/pipelines/{pipeline_id}",
    summary="Get one pipeline",
    responses={
        404: {"detail": "Pipeline Not Found"},
        400: {"detail": "Bad Request"},
        500: {"detail": "Internal Server Error"},
    },
    response_model=PipelineReadWithPipelineStepsAndTasks,
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
        skip_limit_order_by_and_order: SkipLimitOrderByAndOrder = Depends(),
        pipelines_service: PipelinesService = Depends(),
):
    try:
        pipelines = pipelines_service.find_many(
            skip_limit_order_by_and_order.skip,
            skip_limit_order_by_and_order.limit,
            skip_limit_order_by_and_order.order_by,
            skip_limit_order_by_and_order.order,
        )

        return pipelines
    except CompileError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post(
    "/pipelines",
    summary="Create a pipeline",
    responses={
        400: {"detail": "Bad Request"},
        500: {"detail": "Internal Server Error"},
    },
    response_model=PipelineReadWithPipelineStepsAndTasks,
)
def create(
        request: Request,
        pipeline: PipelineCreate,
        pipelines_service: PipelinesService = Depends(),
):

    try:
        pipeline = pipelines_service.create(pipeline, request.app)
    except InconsistentPipelineException as e:
        raise HTTPException(status_code=400, detail=str(e))

    return pipeline


@router.patch(
    "/pipelines/{pipeline_id}",
    summary="Update a pipeline",
    responses={
        404: {"detail": "Pipeline Not Found"},
        500: {"detail": "Internal Server Error"},
    },
    response_model=PipelineReadWithPipelineStepsAndTasks,
)
def update(
        request: Request,
        pipeline_id: UUID,
        pipeline_update: PipelineUpdate,
        pipelines_service: PipelinesService = Depends(),
):
    try:
        pipeline = pipelines_service.update(request.app, pipeline_id, pipeline_update)
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except InconsistentPipelineException as e:
        raise HTTPException(status_code=400, detail=str(e))

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
        request: Request,
        pipeline_id: UUID,
        pipelines_service: PipelinesService = Depends(),
):
    try:
        pipelines_service.delete(pipeline_id, request.app)
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post(
    "/pipeline/check",
    summary="Check if a pipeline is valid",
    responses={
        200: {"valid": True},
        400: {"detail": "Bad Request"},
        500: {"detail": "Internal Server Error"},
    }
)
def check(
        pipeline: PipelineCreate,
        pipelines_service: PipelinesService = Depends(),
):
    try:
        new_pipeline_id = uuid4()
        new_steps = []
        for step in pipeline.steps:
            new_step = PipelineStep(
                identifier=step.identifier,
                needs=step.needs,
                condition=step.condition,
                inputs=step.inputs,
                service_id=step.service_id,
                pipeline_id=new_pipeline_id,
            )
            new_steps.append(new_step)

        new_pipeline = Pipeline(
            id=new_pipeline_id,
            name=pipeline.name,
            description=pipeline.description,
            summary=pipeline.summary,
            steps=new_steps,
            data_in_fields=pipeline.data_in_fields,
            data_out_fields=pipeline.data_out_fields,
        )

        if pipelines_service.check_pipeline_consistency(new_pipeline):
            return {"valid": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
