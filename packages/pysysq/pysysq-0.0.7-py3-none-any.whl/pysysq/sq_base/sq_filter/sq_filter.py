import copy
from typing import Union
from ..sq_clock import SQClock
from ..sq_object import SQObject
from ..sq_logger import SQLogger
from ..sq_queue import SQQueue
from ..sq_plugin import SQHelper


class SQFilter(SQObject):
    def __init__(self, data: dict[str, any]):
        super().__init__(data)
        self.logger = SQLogger(self.__class__.__name__, self.name)

        self.input_q: Union[SQQueue, None] = data.get('input_q', None)
        if self.input_q is None:
            raise ValueError('Input Queue not provided')
        self.output_q: Union[SQQueue, None] = data.get('output_q', None)
        if self.output_q is None:
            raise ValueError('Output Queue not provided')
        self.clk: Union[SQClock, None] = data.get('clk', None)
        if self.clk is None:
            raise ValueError('Clock not provided')
        self.clk.control_flow(self)
        if self.helper is None:
            raise ValueError('Helper not provided')

    def process_packet(self, evt):
        super().process_packet(evt)
        if evt.owner is self.clk:
            pkt = self.input_q.pop()
            if pkt is not None:
                if self.helper.filter_packet(pkt):
                    self.output_q.push(copy.copy(pkt))
                    self.finish_indication(data=evt.data)
        else:
            if evt.name != f'{self.name}_start':
                self.logger.error(f'Ignoring Events other than Clock Events {evt}')
