from typing import Union
from importlib import import_module
import inspect
from .sq_plugin import SQPlugin


class SQPluginLoader:
    def __init__(self, helper_factory):
        self._helper_factory = helper_factory
        self.load_plugin("pysysq.sq_base.sq_plugin.default")

    @staticmethod
    def _import(name: str) -> SQPlugin:
        return import_module(name)  # type: ignore

    def load_plugin(self, plugin_name: str) -> Union[SQPlugin, None]:
        try:
            module = self._import(name=plugin_name)
            module.register(self._helper_factory)

        except Exception as e:
            print(f"Error loading plugin {plugin_name}: {e}")
            return None
