from typing import List
from fastapi import APIRouter, Depends, HTTPException
from .service import TasksService
from common.query_parameters import SkipAndLimit
from .models import TaskRead, TaskUpdate, TaskCreate, Task
from uuid import UUID

router = APIRouter()


@router.get(
    "/tasks/{task_id}",
    summary="Get one task",
    responses={404: {"description": "Task Not Found"}},
    response_model=TaskRead,
)
async def get_one(
        task_id: UUID,
        tasks_service: TasksService = Depends()
):
    task = tasks_service.find_one(task_id)

    if not task:
        raise HTTPException(status_code=404)

    return task


@router.get(
    "/tasks",
    summary="Get many tasks",
    response_model=List[TaskRead],
)
async def get_many_tasks(
        skip_and_limit: SkipAndLimit = Depends(),
        tasks_service: TasksService = Depends(),
):
    tasks = tasks_service.find_many(skip_and_limit.skip, skip_and_limit.limit)

    return tasks


@router.post(
    "/tasks",
    summary="Create a task",
    response_model=TaskRead,
)
async def create(task: TaskCreate, tasks_service: TasksService = Depends()):
    task_create = Task.from_orm(task)
    task = tasks_service.create(task_create)

    return task


@router.patch(
    "/tasks/{task_id}",
    summary="Update a task",
    response_model=TaskRead,
)
async def update(
        task_id: UUID,
        task_update: TaskUpdate,
        tasks_service: TasksService = Depends(),
):
    task = tasks_service.update(task_id, task_update)

    return task


@router.delete(
    "/tasks/{task_id}",
    summary="Delete a task",
    responses={204: {"description": "Successful Deletion"}},
    status_code=204
)
async def delete(
        task_id: UUID,
        tasks_service: TasksService = Depends(),
):
    tasks_service.delete(task_id)
