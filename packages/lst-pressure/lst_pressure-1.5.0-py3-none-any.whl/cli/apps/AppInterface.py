from abc import ABC, abstractmethod
from typing import Self


class AppInterface(ABC):
    @property
    @staticmethod
    def id():
        pass

    @property
    @staticmethod
    def usage():
        pass

    @property
    @staticmethod
    def description():
        pass

    def __init__(self, parser) -> None:
        self.parser = parser
        self.build()

    @abstractmethod
    def build(self) -> Self:
        pass

    @abstractmethod
    def parse(self) -> Self:
        pass

    @abstractmethod
    def exe(self) -> None:
        pass
