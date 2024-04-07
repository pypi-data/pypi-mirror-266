import copy
from typing import Union

from ..sq_event import SQEvent
from ..sq_logger import SQLogger
from ..sq_object import SQObject
from ..sq_queue import SQQueue
from ..sq_plugin import SQHelper


class SQMux(SQObject):
    def __init__(self, data: dict[str, any]):
        super().__init__(data)
        self.logger = SQLogger(self.__class__.__name__, self.name)
        self.input_qs = data.get('input_qs', [])
        if len(self.input_qs) <= 2:
            raise ValueError('At least two input_qs should be provided')
        self.output_q = data.get('output_q', None)
        if self.output_q is None:
            raise ValueError('output_q should be provided')
        self.clk = data.get('clk', None)
        if self.clk is not None:
            self.clk.control_flow(self)
        else:
            raise ValueError('Clock not provided')
        for p in self.input_qs:
            if p is not None:
                if not isinstance(p, SQQueue):
                    raise ValueError(f'queues should contain  SQQueue object ,'
                                     f' got {type(p)} instead.')

            else:
                raise ValueError('Null Queue Provided')
        if self.helper is None:
            raise ValueError('Helper not provided')
        self.current_port = None

    def process_packet(self, evt):
        super().process_packet(evt)
        if evt.owner is self.clk:
            self.current_port = self.helper.select_input_queue()
            if self.current_port is not None:
                curr_pkt = self.current_port.pop()
                if curr_pkt is not None:
                    self.output_q.push(copy.copy(curr_pkt))
                    self.finish_indication()
        else:
            if evt.name != f'{self.name}_start':
                self.logger.error(f'Ignoring Events other than Clock Events {evt}')

    def process_data(self, evt: SQEvent):
        super().process_data(evt)
        self.helper.process_data(evt,self.tick)
