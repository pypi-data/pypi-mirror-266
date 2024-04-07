import copy
from typing import List
from ..sq_object import SQObject
from ..sq_queue import SQQueue
from ..sq_logger import SQLogger
from ..sq_clock import SQClock


class SQSplitter(SQObject):
    def __init__(self, data: dict[str, any]):
        super().__init__(data)
        self.logger = SQLogger(self.__class__.__name__, self.name)
        self.output_qs = data.get('output_qs', [])
        if len(self.output_qs) < 2:
            raise ValueError('At least two output_qs should be provided')
        self.input_q = data.get('input_q', None)
        if self.input_q is None:
            raise ValueError('input_q should be provided')
        self.clk = data.get('clk', None)

        if self.clk is not None:
            self.clk.control_flow(self)
        else:
            raise ValueError('Clock not provided')
        for p in self.output_qs:
            if not isinstance(p, SQQueue):
                raise ValueError(f'rx_q should be a SQQueue object , got {type(p)} instead.')

    def process_packet(self, evt):
        super().process_packet(evt)
        if evt.owner is self.clk:
            pkt = self.input_q.pop()
            for q in self.output_qs:
                if pkt is not None:
                    self.logger.info(f'Pushing Packet {evt.data} to Queue {q.name}')
                    q.push(copy.copy(pkt))
            self.finish_indication()
        else:
            if evt.name != f'{self.name}_start':
                self.logger.error(f'Ignoring Events other than Clock Event {evt}')
