from logger import Logger
from storage import Storage

from fastapi import Depends

from sqlalchemy.orm import Session

from database import get_db


class StatsService:
    def __init__(self, logger: Logger = Depends(), storage: Storage = Depends(), db: Session = Depends(get_db)):
        self.logger = logger
        self.storage = storage
        self.db = db
    # TODO: Implement stats method
    def stats(self):
        stats = None

        return stats
