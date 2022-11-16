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

    def find_many(self, skip: int = 0, limit: int = 100) -> list[TaskModel] :
        self.logger.info("Find many tasks")
        return self.db.query(TaskModel).offset(skip).limit(limit).all()

    def create(self):
        self.logger.info("Create task")
        task = TaskModel()
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)

        return task

    def find_first(self):
        self.logger.info("Find first task")

    def update(self):
        self.logger.info("Update task")

    def delete(self):
        self.logger.info("Delete task")
