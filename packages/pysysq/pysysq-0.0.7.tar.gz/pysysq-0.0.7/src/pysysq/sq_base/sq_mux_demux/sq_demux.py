import copy
from typing import List, Union
from ..sq_object import SQObject
from ..sq_queue import SQQueue
from ..sq_clock import SQClock
from ..sq_logger import SQLogger
from ..sq_plugin import SQHelper
from ..sq_event import SQEvent


class SQDemux(SQObject):
    def __init__(self, data: dict[str, any]):
        super().__init__(data)
        self.logger = SQLogger(self.__class__.__name__, self.name)
        self.output_qs: List[SQQueue] = data.get('output_qs', [])
        self.input_q: Union[SQQueue, None] = data.get('input_q', None)
        self.clk: Union[SQClock, None] = data.get('clk', None)
        if self.clk is not None:
            self.clk.control_flow(self)
        else:
            raise ValueError('input_q should be provided')
        if self.input_q is None:
            raise ValueError('input_q should be provided')
        if len(self.output_qs) < 2:
            raise ValueError('At least two output queue should be provided')

        for p in self.output_qs:
            if not isinstance(p, SQQueue):
                raise TypeError(f'queues should contain SQQueue, got {type(p)} instead.')
        if not isinstance(self.input_q, SQQueue):
            raise TypeError(f'input_q should be a SQQueue object , got {type(self.input_q)} instead.')
        if self.helper is None:
            raise ValueError('Helper not provided')
        self.current_port = 0

    def process_packet(self, evt):
        super().process_packet(evt)
        if evt.owner is self.clk:
            curr_pkt = self.input_q.pop()
            self.current_port = self.helper.select_output_queue(curr_pkt)
            if self.current_port is not None:
                if curr_pkt is not None:
                    self.current_port.push(copy.copy(curr_pkt))
                    self.finish_indication()
            else:
                self.logger.error(f'No Queue Selected for {evt.data}')
        else:
            if evt.name != f'{self.name}_start':
                self.logger.error(f'Ignoring Events other than clk events {evt}')

    def process_data(self, evt: SQEvent):
        super().process_data(evt)
        self.helper.process_data(evt,self.tick)
