from typing import List
from fastapi import APIRouter, Depends, HTTPException
from common.exceptions import NotFoundException, UnprocessableEntityException
from pipeline_steps.service import PipelineStepsService
from common.query_parameters import SkipLimitOrderByAndOrder
from pipeline_steps.models import PipelineStep, PipelineStepRead, PipelineStepUpdate, PipelineStepCreate
from uuid import UUID

router = APIRouter()


@router.get(
    "/pipeline-steps/{pipeline_step_id}",
    summary="Get one pipeline step",
    responses={
        404: {"detail": "Pipeline Step Not Found"},
        400: {"detail": "Bad Request"},
        500: {"detail": "Internal Server Error"},
    },
    response_model=PipelineStepRead,
)
def get_one(
        pipeline_step_id: UUID,
        pipeline_steps_service: PipelineStepsService = Depends()
):
    pipeline_step = pipeline_steps_service.find_one(pipeline_step_id)
    if not pipeline_step:
        raise HTTPException(status_code=404, detail="Pipeline Step Not Found")

    return pipeline_step


@router.get(
    "/pipeline-steps",
    summary="Get many pipeline steps",
    response_model=List[PipelineStepRead],
)
def get_many_pipelines(
        skip_limit_order_by_and_order: SkipLimitOrderByAndOrder = Depends(),
        pipeline_steps_service: PipelineStepsService = Depends(),
):
    pipeline_steps = pipeline_steps_service.find_many(
        skip_limit_order_by_and_order.skip,
        skip_limit_order_by_and_order.limit,
        skip_limit_order_by_and_order.order_by,
        skip_limit_order_by_and_order.order,
    )

    return pipeline_steps


@router.post(
    "/pipeline-steps",
    summary="Create a pipeline step",
    response_model=PipelineStepRead,
)
def create(
    pipeline_step: PipelineStepCreate,
    pipeline_steps_service: PipelineStepsService = Depends(),
):
    try:
        pipeline_step_create = PipelineStep.model_validate(pipeline_step)
        pipeline_step = pipeline_steps_service.create(pipeline_step_create)
    except UnprocessableEntityException as e:
        raise HTTPException(status_code=422, detail=str(e))

    return pipeline_step


@router.patch(
    "/pipeline-steps/{pipeline_step_id}",
    summary="Update a pipeline step",
    responses={
        404: {"detail": "Pipeline Step Not Found"},
        500: {"detail": "Internal Server Error"},
    },
    response_model=PipelineStepRead,
)
def update(
        pipeline_id: UUID,
        pipeline_step_update: PipelineStepUpdate,
        pipeline_steps_service: PipelineStepsService = Depends(),
):
    try:
        pipeline_step = pipeline_steps_service.update(pipeline_id, pipeline_step_update)
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))

    return pipeline_step


@router.delete(
    "/pipeline-steps/{pipeline_step_id}",
    summary="Delete a pipeline step",
    responses={
        204: {"detail": "Pipeline Step Removed"},
        404: {"detail": "Pipeline Step Not Found"},
        500: {"detail": "Internal Server Error"},
    },
    status_code=204
)
def delete(
        pipeline_step_id: UUID,
        pipeline_steps_service: PipelineStepsService = Depends(),
):
    try:
        pipeline_steps_service.delete(pipeline_step_id)
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
