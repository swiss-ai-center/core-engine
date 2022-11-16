from fastapi import APIRouter, Depends
from .service import TasksService
from .schemas.task import TaskSchema

router = APIRouter()


@router.get("/tasks", summary="Find many tasks", description="Find many tasks.", response_model=list[TaskSchema])
async def find_many(tasks_service: TasksService = Depends()):
    tasks = tasks_service.find_many()

    dtos = []

    for task in tasks:
        taskDto = TaskSchema.toTaskSchema(task)
        dtos.append(taskDto)

    return dtos

@router.post("/tasks", summary="Create a task", description="Create a task.", response_model=TaskSchema)
async def create(tasks_service: TasksService = Depends()):
    task = tasks_service.create()

    dto = TaskSchema.toTaskSchema(task)

    return dto
