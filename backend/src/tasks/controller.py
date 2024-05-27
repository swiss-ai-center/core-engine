from typing import List
from fastapi import APIRouter, Depends, HTTPException
from common.exceptions import NotFoundException
from tasks.enums import TaskStatus
from tasks.service import TasksService
from common.query_parameters import QueryParameters
from tasks.models import TaskRead, TaskUpdate, TaskCreate, Task, TaskReadWithServiceAndPipeline
from uuid import UUID

router = APIRouter()


@router.get(
    "/tasks/{task_id}",
    summary="Get one task",
    responses={
        404: {"detail": "Task Not Found"},
        400: {"detail": "Bad Request"},
        500: {"detail": "Internal Server Error"},
    },
    response_model=TaskReadWithServiceAndPipeline,
)
def get_one(
        task_id: UUID,
        tasks_service: TasksService = Depends()
):
    task = tasks_service.find_one(task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task Not Found")

    return task


@router.get(
    "/tasks/{task_id}/status",
    summary="Get one task status",
    responses={
        404: {"detail": "Task Not Found"},
        400: {"detail": "Bad Request"},
        500: {"detail": "Internal Server Error"},
    },
    response_model=TaskStatus,
)
async def get_one_status(
        task_id: UUID,
        tasks_service: TasksService = Depends()
):
    task = tasks_service.find_one(task_id)

    if not task:
        raise HTTPException(status_code=404, detail="Task Not Found")
    else:
        if task.status == "pending":
            task = await tasks_service.get_status_from_service(task)

    return task.status


@router.get(
    "/tasks",
    summary="Get many tasks",
    response_model=List[TaskRead],
)
def get_many_tasks(
        query_parameters: QueryParameters = Depends(),
        tasks_service: TasksService = Depends(),
):
    tasks = tasks_service.find_many(
        query_parameters.skip,
        query_parameters.limit,
        query_parameters.order_by,
        query_parameters.order,
    )

    return tasks


@router.post(
    "/tasks",
    summary="Create a task",
    response_model=TaskReadWithServiceAndPipeline,
)
def create(task: TaskCreate, tasks_service: TasksService = Depends()):
    task_create = Task.model_validate(task)
    task = tasks_service.create(task_create)

    return task


@router.patch(
    "/tasks/{task_id}",
    summary="Update a task",
    responses={
        404: {"detail": "Task Not Found"},
        500: {"detail": "Internal Server Error"},
    },
    response_model=TaskReadWithServiceAndPipeline,
)
async def update(
        task_id: UUID,
        task_update: TaskUpdate,
        tasks_service: TasksService = Depends(),
):
    try:
        # Update the task
        task: Task = await tasks_service.update(task_id, task_update)

        # Check if the task is linked to a pipeline_execution
        if task.pipeline_execution_id:
            if task.status == TaskStatus.ERROR:
                # If the task is in error, we need to stop the pipeline_execution
                if task.pipeline_execution_id is not None:
                    await tasks_service.stop_pipeline_execution(task)
            else:
                # If the task is linked to a pipeline_execution, we need launch the next step in the pipeline
                await tasks_service.launch_next_step_in_pipeline(task)

    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))

    return task


@router.delete(
    "/tasks/{task_id}",
    summary="Delete a task",
    responses={
        204: {"detail": "Task Removed"},
        404: {"detail": "Task Not Found"},
        500: {"detail": "Internal Server Error"},
    },
    status_code=204
)
def delete(
        task_id: UUID,
        tasks_service: TasksService = Depends(),
):
    try:
        tasks_service.delete(task_id)
    except NotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
