from abc import ABC, abstractmethod
from idbt.manifest.base import BaseDefinition

"""
parser file content to definition
"""


class BaseParser(ABC):
    def __init__(self) -> None:
        super().__init__()

    @abstractmethod
    def parse(self) -> BaseDefinition:
        pass
