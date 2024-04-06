import datetime
from abc import ABC, abstractmethod


class Storage(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def update_register(self, id: str, data: dict) -> bool:
        pass

    @abstractmethod
    def get_register(self, id: str) -> bool:
        pass

    @abstractmethod
    def create_register(self, id: str) -> bool:
        pass

    def create_first_register(self) -> dict:
        return {
            "count": 1,
            "date": str(datetime.datetime.now()),
            "last": str(datetime.datetime.now()),
        }
