from typing import List, Union
import copy

from .sq_event import SQEvent
from ..sq_logger import SQLogger
from ..sq_time_base import SQTimeBase


class SQEventQueue:
    def __init__(self, name: str = ""):
        self.name = name
        self.queue: List[SQEvent] = []
        self.logger = SQLogger(self.__class__.__name__, name)

    def set_log_level(self, level):
        self.logger.set_level(level)

    def schedule(self, _event: SQEvent):

        self.queue.append(copy.copy(_event))

    def pop_next_event(self) -> Union[SQEvent, None]:
        if len(self.queue) > 0:
            evt = self.get_next_event()
            if evt is not None:
                self.logger.debug(f'pop event  {evt.name} ')
                self.queue.remove(evt)
            return evt
        else:
            return None

    def get_next_event(self):
        evt = None
        if len(self.queue) > 0:
            current_time = SQTimeBase.get_current_sim_time()
            possible_events = [k for k in self.queue if k.scheduled_tick <= current_time]
            if len(possible_events) > 0:
                evt = min(possible_events, key=lambda x: x.scheduled_tick)
        return evt
