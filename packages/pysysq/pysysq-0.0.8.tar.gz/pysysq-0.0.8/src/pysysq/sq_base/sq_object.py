from abc import ABC
from typing import List, Union

from .sq_event import SQEvent, SQEventManager, EventType
from .sq_logger import SQLogger
from .sq_statistics import SQStatistics
from .sq_packet import SQMetadata
from .sq_plugin import SQHelper


class SQObject(ABC):
    """
    Base class for all objects in the simulation
    """

    def __init__(self, data: dict[str, any]):

        self.name = data.get('name', "")
        self.helper_factory= data.get('helper_factory', None)
        if self.helper_factory is None:
            raise ValueError('helper_factory should be provided')
        self.helper_name = data.get('helper', "default")
        self.helper: Union[SQHelper, None] = None
        data['owner'] = self
        self.helper = self.helper_factory.create(name=self.helper_name, data=data)
        if self.name == "":
            raise ValueError('name should be provided')
        self.evt_q: int = data.get('event_q', 0)
        self.logger = SQLogger(self.__class__.__name__, self.name)
        self.event_manager = data.get('event_mgr', None)
        if self.event_manager is None:
            raise ValueError('event_mgr should be provided')
        self.tick: int = 0
        self.self_starting = False
        self.children = data.get('children', [])
        self.statistics = SQStatistics()
        self.statistics_properties = []
        self.is_self_ticking: bool = data.get('is_self_ticking', False)
        self.data_flow_map = []
        self.tick_evt = SQEvent(_name=f'{self.name}_tick',
                                owner=self)
        self.tick_evt.type = EventType.TICK_EVENT

        self.start_evt = SQEvent(_name=f'{self.name}_start',
                                 owner=self)
        self.start_evt.type = EventType.START_EVT
        self.start_evt.add_handler(self.process_packet)
        self.finish_evt = SQEvent(_name=f'{self.name}_finish',
                                  owner=self)
        self.finish_evt.type = EventType.PROCESS_EVT

        self.metadata_evt = SQEvent(_name=f'{self.name}_metadata',
                                    owner=self)

        self.metadata_evt.type = EventType.METADATA_EVT

    def __repr__(self):
        return self.name

    def set_log_level(self, level):
        self.logger.set_level(level)

    def subscribe_metadata(self, owner: str, data_name: str):
        if owner is self.name:
            self.logger.error(f"Cannot subscribe to metadata from other objects")
            return
        else:
            self.data_flow_map.append(SQMetadata(owner=owner, name=data_name, value=None))

    def _is_metadata_subscribed(self, owner: str, data_name: str):
        for data in self.data_flow_map:
            if data.owner == owner and data.name == data_name:
                return True
        return False

    def get_metadata_received(self, owner: str, data_name: str):
        for data in self.data_flow_map:
            if data.owner == owner and data.name == data_name:
                return data.value
        return None

    def update_subscribed_metadata(self, metadata: SQMetadata):
        for data in self.data_flow_map:
            if data.owner == metadata.owner and data.name == metadata.name:
                data.value = metadata.value

    def register_property(self, name: str, owner=None):
        if owner is not None:
            self.statistics_properties.append({'owner': owner, 'name': name})
        else:
            self.statistics_properties.append({'owner': self, 'name': name})

    def process_data(self, evt: SQEvent):
        self.logger.info(f'Process Metadata {evt.owner.name}::{evt.data.name} on Tick {self.tick}')

    def _process_metadata(self, evt: SQEvent):
        if evt.type == EventType.METADATA_EVT:
            if evt.data is not None:
                if isinstance(evt.data, SQMetadata):
                    if self._is_metadata_subscribed(evt.data.owner, evt.data.name):
                        self.update_subscribed_metadata(evt.data)
                        self.process_data(evt)
                else:
                    self.logger.error(f"Metadata {evt.data} not a SQMetadata object")
        else:
            self.logger.error(f"Ignoring Metadata Event {evt.name} from {evt.owner.name}")

    def init(self):
        self.logger.info(f'init')
        for child in self.children:
            assert isinstance(child, SQObject), "all child objects of an SQObject must be derived from SQObject"
            child.init()

    def deinit(self):
        self.logger.info(f'deinit')
        for child in self.children:
            child.deinit()

    def read_statistics(self):
        return self.statistics

    def start(self):
        self.logger.info(f'start')
        if not self.self_starting:
            self.event_manager.schedule(self.start_evt, when=1)
        if self.is_self_ticking:
            self.logger.info(f'is self ticking')
            self.self_connect()
        self.tick = 0
        for child in self.children:
            child.start()

    def finish_indication(self, data=None, when=1):
        self.logger.info(f'finish indication')
        self.finish_evt.data = data
        self.event_manager.schedule(self.finish_evt, when=when)

    def data_indication(self, data: SQMetadata, when=1):
        self.logger.info(f'data indication')
        self.metadata_evt.data = data
        self.event_manager.schedule(self.metadata_evt, when=when)

    def self_trigger(self, when=1):
        self.logger.info(f'self_trigger at {self.tick}')
        self.event_manager.schedule(self.tick_evt, when=when)

    def collect_statistics(self):
        for p in self.statistics_properties:
            self.statistics.add(p['name'], getattr(p['owner'], p['name']), self.name)

    def process_packet(self, evt: SQEvent):
        self.logger.info(f'Process Event {evt.owner.name}::{evt.name} on Tick {self.tick}')
        if self.is_self_ticking:
            self.self_trigger()
        self.collect_statistics()

    def control_flow(self, obj: "SQObject", **kwargs):
        self.finish_evt.add_handler(obj.process_packet)
        return obj

    def data_flow(self, obj: "SQObject", metadata: List[str]):
        self.metadata_evt.add_handler(obj._process_metadata)
        for data in metadata:
            obj.subscribe_metadata(owner=self.name, data_name=data)
        return obj

    def self_connect(self):
        self.tick_evt.add_handler(self.process_packet)

    def disconnect_control_flow(self, obj: "SQObject"):
        self.logger.info(f"disconnecting the observer{obj.name} from control flow")
        self.finish_evt.remove_handler(obj.process_packet)

    def disconnect_data_flow(self, obj: "SQObject"):
        self.logger.info(f"disconnecting the observer{obj.name} from dataflow")
        self.metadata_evt.remove_handler(obj._process_metadata)

    def get_current_tick(self):
        return self.tick

    def update_tick(self, ticks: int):
        self.tick += ticks
        self.logger.info(f'Updating Current Tick {self.tick}')
