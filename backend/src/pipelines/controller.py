from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import PlainTextResponse
from common.exceptions import NotFoundException, InconsistentPipelineException, ConflictException
from pipelines.service import PipelinesService
from common.query_parameters import QueryParameters
from pipelines.models import PipelineRead, PipelineUpdate, PipelineCreate, Pipeline, \
    PipelineReadWithPipelineStepsAndTasks, PipelinesWithCount
from pipeline_steps.models import PipelineStep
from uuid import UUID, uuid4
from sqlalchemy.exc import CompileError
import textwrap

from services.service import ServicesService
from authentication.functions import RoleChecker, get_optional_current_user
from authentication.models import Role, User
from services.access import ServiceAccessLevel, accessible_service_levels

router = APIRouter()


def require_pipeline_access(
        pipeline: Pipeline | None,
        current_user: User | None,
        pipelines_service: PipelinesService,
) -> Pipeline:
    access_levels = accessible_service_levels(current_user.role if current_user else None)
    if not pipeline or not pipelines_service.is_accessible(pipeline, access_levels):
        raise HTTPException(status_code=404, detail="Pipeline Not Found")
    return pipeline


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
        current_user: User | None = Depends(get_optional_current_user),
        pipelines_service: PipelinesService = Depends()
):
    return require_pipeline_access(pipelines_service.find_one(pipeline_id), current_user, pipelines_service)


@router.get(
    "/pipelines/slug/{pipeline_slug}",
    summary="Get one pipeline by slug",
    responses={
        404: {"detail": "Pipeline Not Found"},
        400: {"detail": "Bad Request"},
        500: {"detail": "Internal Server Error"},
    },
    response_model=PipelineReadWithPipelineStepsAndTasks,
)
def get_one_by_slug(
        pipeline_slug: str,
        current_user: User | None = Depends(get_optional_current_user),
        pipelines_service: PipelinesService = Depends()
):
    return require_pipeline_access(pipelines_service.find_one_by_slug(pipeline_slug), current_user, pipelines_service)


@router.get(
    "/pipelines/slug/{pipeline_slug}/code-snippet",
    summary="Get one code snippet by slug to use the service externally",
    responses={
        404: {"detail": "Service Not Found"},
        400: {"detail": "Bad Request"},
        500: {"detail": "Internal Server Error"},
    },
    response_class=PlainTextResponse,
)
async def get_code_snippet_by_slug(
        pipeline_slug: str,
        current_user: User | None = Depends(get_optional_current_user),
        pipelines_service: PipelinesService = Depends()
):
    service = require_pipeline_access(
        pipelines_service.find_one_by_slug(pipeline_slug),
        current_user,
        pipelines_service,
    )

    raw_snippet = pipelines_service.generate_code_snippet(service)

    # Format the code snippet
    formatted_snippet = textwrap.dedent(raw_snippet).strip()

    return formatted_snippet


@router.get(
    "/pipelines",
    summary="Get many pipelines",
    response_model=PipelinesWithCount | List[PipelineRead],
)
def get_many_pipelines(
        with_count: bool = False,
        query_parameters: QueryParameters = Depends(),
        current_user: User | None = Depends(get_optional_current_user),
        pipelines_service: PipelinesService = Depends(),
):
    try:
        if query_parameters.search:
            query_parameters.search = query_parameters.search.lower()

        if with_count:
            count, pipelines = pipelines_service.find_many_with_total_count(
                query_parameters.search,
                query_parameters.skip,
                query_parameters.limit,
                query_parameters.order_by,
                query_parameters.order,
                query_parameters.tags,
                query_parameters.status,
                accessible_service_levels(current_user.role if current_user else None),
            )

            return PipelinesWithCount(count=count, pipelines=pipelines)
        else:
            pipelines = pipelines_service.find_many(
                query_parameters.search,
                query_parameters.skip,
                query_parameters.limit,
                query_parameters.order_by,
                query_parameters.order,
                query_parameters.tags,
                query_parameters.status,
                accessible_service_levels(current_user.role if current_user else None),
            )

            return pipelines

    except CompileError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get(
    "/admin/pipelines",
    summary="List every pipeline for administration",
    response_model=PipelinesWithCount,
    responses={
        401: {"detail": "Unauthorized"},
        403: {"detail": "Administrator access required"},
    },
)
def get_admin_pipelines(
        query_parameters: QueryParameters = Depends(),
        _current_admin: User = Depends(RoleChecker([Role.ADMIN])),
        pipelines_service: PipelinesService = Depends(),
):
    count, pipelines = pipelines_service.find_many_with_total_count(
        query_parameters.search,
        query_parameters.skip,
        query_parameters.limit,
        query_parameters.order_by,
        query_parameters.order,
        query_parameters.tags,
        query_parameters.status,
        list(ServiceAccessLevel),
    )
    return PipelinesWithCount(count=count, pipelines=pipelines)


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
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ConflictException as e:
        raise HTTPException(status_code=409, detail=str(e))

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
    except ConflictException as e:
        raise HTTPException(status_code=409, detail=str(e))

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
        services_service: ServicesService = Depends(),
):
    try:
        flat_steps, flat_data_out = pipelines_service.expand_nested_pipelines(
            pipeline.steps, pipeline.data_out_fields, parent_slug=pipeline.slug
        )

        new_pipeline_id = uuid4()
        new_steps = []
        for step in flat_steps:
            service = services_service.find_one_by_slug(step.service_slug)
            if not service:
                raise NotFoundException(f"Service with slug {step.service_slug} not found")
            new_pipeline_step = PipelineStep(
                identifier=step.identifier,
                needs=step.needs,
                condition=step.condition,
                inputs=step.inputs,
                pipeline_id=new_pipeline_id,
                service_id=service.id,
            )
            new_steps.append(PipelineStep.model_validate(new_pipeline_step))

        new_pipeline = Pipeline(
            id=new_pipeline_id,
            name=pipeline.name,
            description=pipeline.description,
            summary=pipeline.summary,
            steps=new_steps,
            data_in_fields=pipeline.data_in_fields,
            data_out_fields=flat_data_out,
        )

        if pipelines_service.check_pipeline_consistency(new_pipeline):
            return {"valid": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
