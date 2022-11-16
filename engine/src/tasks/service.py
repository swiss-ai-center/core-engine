from fastapi import Depends
from storage import Storage
from sqlalchemy.orm import Session
from database import get_db
from logger import Logger
from .models.task import TaskModel


class TasksService:
    def __init__(self, logger: Logger = Depends(), storage: Storage = Depends(), db: Session = Depends(get_db)):
        self.logger = logger
        self.storage = storage
        self.db = db

    def find_many(self, skip: int = 0, limit: int = 100) -> list[TaskModel]:
        self.logger.debug("Find many tasks")
        return self.db.query(TaskModel).offset(skip).limit(limit).all()

    def create(self):
        self.logger.debug("Creating task")
        task = TaskModel()
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        self.logger.debug(f"Created task with id {task.id}")

        return task

    def find_one(self, task_id: int) -> TaskModel:
        self.logger.debug("Find first task")
        return self.db.query(TaskModel).get(task_id)

    # TODO: Implement update method
    def update(self):
        self.logger.debug("Update task")

    # TODO: Implement delete method
    def delete(self):
        self.logger.debug("Delete task")
