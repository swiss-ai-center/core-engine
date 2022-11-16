from fastapi import Depends
from storage import Storage
from sqlalchemy.orm import Session
from database import get_db
from logger import Logger


class PipelinesService:
    def __init__(self, logger: Logger = Depends(), storage: Storage = Depends(), db: Session = Depends(get_db)):
        self.logger = logger
        self.storage = storage
        self.db = db

    # TODO: Implement get_services method
    def get_pipelines(self):
        pipelines = None

        return pipelines

    # TODO: Implement create method
    def create(self, pipeline_name, pipeline):
        pass

    # TODO: Implement delete method
    def delete(self, pipeline_name):
        pass

    # TODO: Implement find_one method
    def find_one(self, pipeline_name):
        pipeline = None

        return pipeline
