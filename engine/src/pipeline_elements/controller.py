from typing import List
from fastapi import APIRouter, Depends, HTTPException
from common.exceptions import NotFoundException, UnprocessableEntityException
from pipeline_elements.service import PipelineElementsService
from common.query_parameters import SkipAndLimit
from pipeline_elements.models import PipelineElement, PipelineElementRead, PipelineElementUpdate, PipelineElementCreate
from uuid import UUID

router = APIRouter()


@router.get(
    "/pipeline-elements/{pipeline_element_id}",
    summary="Get one pipeline element",
    responses={
        404: {"detail": "Pipeline Element Not Found"},
        400: {"detail": "Bad Request"},
        500: {"detail": "Internal Server Error"},
    },
    response_model=PipelineElementRead,
)
def get_one(
        pipeline_element_id: UUID,
        pipeline_elements_service: PipelineElementsService = Depends()
):
    pipeline_element = pipeline_elements_service.find_one(pipeline_element_id)
    if not pipeline_element:
        raise HTTPException(status_code=404, detail="Pipeline Element Not Found")

    return pipeline_element


@router.get(
    "/pipeline-elements",
    summary="Get many pipeline elements",
    response_model=List[PipelineElementRead],
)
def get_many_pipelines(
        skip_and_limit: SkipAndLimit = Depends(),
        pipeline_elements_service: PipelineElementsService = Depends(),
):
    pipeline_elements = pipeline_elements_service.find_many(skip_and_limit.skip, skip_and_limit.limit)

    return pipeline_elements


@router.post(
    "/pipeline-elements",
    summary="Create a pipeline element",
    response_model=PipelineElementRead,
)
def create(
    pipeline: PipelineElementCreate,
    pipeline_elements_service: PipelineElementsService = Depends(),
):
    try:
        pipeline_element_create = PipelineElement.from_orm(pipeline)
        pipeline_element = pipeline_elements_service.create(pipeline_element_create)
    except UnprocessableEntityException as e:
        raise HTTPException(status_code=422, detail=str(e))

    return pipeline_element


@router.patch(
    "/pipeline-elements/{pipeline_element_id}",
    summary="Update a pipeline element",
    responses={
        404: {"detail": "Pipeline Element Not Found"},
        500: {"detail": "Internal Server Error"},
    },
    response_model=PipelineElementRead,
)
def update(
        pipeline_id: UUID,
        pipeline_element_update: PipelineElementUpdate,
        pipeline_elements_service: PipelineElementsService = Depends(),
):
    try:
        pipeline_element = pipeline_elements_service.update(pipeline_id, pipeline_element_update)
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))

    return pipeline_element


@router.delete(
    "/pipeline-elements/{pipeline_element_id}",
    summary="Delete a pipeline element",
    responses={
        204: {"detail": "Pipeline Element Removed"},
        404: {"detail": "Pipeline Element Not Found"},
        500: {"detail": "Internal Server Error"},
    },
    status_code=204
)
def delete(
        pipeline_element_id: UUID,
        pipeline_elements_service: PipelineElementsService = Depends(),
):
    try:
        pipeline_elements_service.delete(pipeline_element_id)
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
