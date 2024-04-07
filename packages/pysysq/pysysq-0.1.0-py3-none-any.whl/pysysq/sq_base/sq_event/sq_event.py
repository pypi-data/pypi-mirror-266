from enum import Enum
from typing import Callable


class EventType(Enum):
    START_EVT = 0
    PROCESS_EVT = 1
    METADATA_EVT = 2
    TICK_EVENT = 3


class SQEvent:
    def __init__(self, _name: str, owner):
        self.name = _name
        self.owner = owner
        self.sim_queuing_timestamp = 0
        self.sim_processing_timestamp = 0
        self.host_timestamp = None
        self.scheduled_tick = 0
        self.data = None
        self.type:EventType = EventType.PROCESS_EVT
        self.actions = []

    def add_handler(self, action: Callable):
        if action not in self.actions:
            self.actions.append(action)

    def remove_handler(self, action: Callable):
        self.actions.remove(action)

    def has_handlers(self):
        return len(self.actions) > 0

    def __repr__(self):
        return self.name
