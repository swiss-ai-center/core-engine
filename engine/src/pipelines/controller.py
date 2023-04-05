from typing import List
from fastapi import APIRouter, Depends, HTTPException
from common.exceptions import NotFoundException, InconsistentPipelineException
from pipelines.service import PipelinesService
from common.query_parameters import SkipAndLimit
from pipelines.models import PipelineRead, PipelineUpdate, PipelineCreate, Pipeline, \
    PipelineReadWithPipelineStepsAndTasks
from pipeline_steps.models import PipelineStep
from uuid import UUID, uuid4

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
        skip_and_limit: SkipAndLimit = Depends(),
        pipelines_service: PipelinesService = Depends(),
):
    pipelines = pipelines_service.find_many(skip_and_limit.skip, skip_and_limit.limit)

    return pipelines


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
        pipeline: PipelineCreate,
        pipelines_service: PipelinesService = Depends(),
):

    try:
        # pipeline_steps = pipeline.steps
        # pipeline_create = Pipeline.from_orm(pipeline)
        # # We need to add the steps to the pipeline before creating it because the orm removed them since they are not
        # # The same type as in the model
        # print(pipeline_steps)
        # pipeline_create.steps = pipeline_steps
        # print(pipeline_create)
        pipeline = pipelines_service.create(pipeline)
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
                execution_unit_id=step.execution_unit_id,
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
