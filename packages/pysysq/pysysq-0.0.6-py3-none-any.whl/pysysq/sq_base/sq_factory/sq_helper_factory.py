
from typing import Callable, Any
from ..sq_plugin import SQHelper


class SQHelperFactory:
    def __init__(self):
        self.factory_map: dict[str, Callable[..., SQHelper]] = {}

    def register(self, name, factory):
        self.factory_map[name] = factory

    def create(self, name, data: dict[str, Any]) -> SQHelper:
        return self.factory_map[name](data)
