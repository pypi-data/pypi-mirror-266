from typing import Callable, Any, List, Union
from ..sq_object import SQObject
from ..sq_clock import SQClock
from ..sq_filter import SQFilter
from ..sq_merger import SQMerger
from ..sq_mux_demux import SQMux, SQDemux
from ..sq_pkt_gen import SQPacketGenerator
from ..sq_pkt_processor import SQPktProcessor
from ..sq_simulator import SQSimulator
from ..sq_splitter import SQSplitter
from ..sq_pkt_sink import SQPktSink
from ..sq_plugin import SQPluginLoader
from .sq_helper_factory import SQHelperFactory
from ..sq_queue import SQSingleQueue
from ..sq_event import SQEventManager
class SQFactory:
    def __init__(self, helper_factory: SQHelperFactory = None,
                 plugin_list: Union[List[str], None] = None):
        if plugin_list is None:
            self.plugin_list = []
        else:
            self.plugin_list = plugin_list
        self.factory_map: dict[str, Callable[..., SQObject]] = {
            'SQClock': SQClock,
            'SQFilter': SQFilter,
            'SQMerger': SQMerger,
            'SQMux': SQMux,
            'SQDemux': SQDemux,
            'SQPacketGenerator': SQPacketGenerator,
            'SQPktProcessor': SQPktProcessor,
            'SQSimulator': SQSimulator,
            'SQSplitter': SQSplitter,
            'SQPktSink': SQPktSink,
            'SQQueue': SQSingleQueue,
        }
        self.event_mgr = SQEventManager()
        self.helper_factory = helper_factory
        if self.helper_factory is None:
            self.helper_factory = SQHelperFactory()
        self.plugin_loader = SQPluginLoader(self.helper_factory)
        for plugin in self.plugin_list:
            self.load_plugin(plugin)

    def load_plugin(self, plugin_name: str) -> None:
        self.plugin_loader.load_plugin(plugin_name)

    def create(self, obj_type: str, data: dict[str, Any]) -> SQObject:
        data['helper_factory'] = self.helper_factory
        data['event_mgr'] = self.event_mgr
        return self.factory_map[obj_type](data)
