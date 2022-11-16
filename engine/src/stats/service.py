from logger import Logger
from storage import Storage
from fastapi import Depends
from sqlmodel import Session
from database import get_session


class StatsService:
    def __init__(self, logger: Logger = Depends(), storage: Storage = Depends(), session: Session = Depends(get_session)):
        self.logger = logger
        self.storage = storage
        self.session = session
    # TODO: Implement stats method
    def stats(self):
        stats = None

        return stats
