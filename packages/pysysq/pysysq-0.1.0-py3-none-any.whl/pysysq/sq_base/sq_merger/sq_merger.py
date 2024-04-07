from typing import List
from ..sq_object import SQObject
from ..sq_queue import SQQueue
from ..sq_logger import SQLogger
from ..sq_clock import SQClock


class SQMerger(SQObject):
    def __init__(self, data: dict[str, any]):
        super().__init__(data)
        self.logger = SQLogger(self.__class__.__name__, self.name)
        self.input_qs = data.get('input_qs', [])
        self.output_q = data.get('output_q', None)
        if self.output_q is None:
            raise ValueError('output_q should be provided')
        self.clk = data.get('clk', None)
        if self.clk is not None:
            self.clk.control_flow(self)
        if len(self.input_qs) <= 2:
            raise ValueError('At least two input_qs should be provided')
        if self.output_q is None:
            raise ValueError('tx_queue should be provided')
        for p in self.input_qs:
            if not isinstance(p, SQQueue):
                raise ValueError(f'input_q should be a SQQueue object , got {type(p)} instead.')
        if not isinstance(self.output_q, SQQueue):
            raise ValueError(f'output_q should be a SQQueue object , got {type(self.output_q)} instead.')

    def process_packet(self, evt):
        super().process_packet(evt)
        if evt.owner is self.clk:
            for q in self.input_qs:
                if q.peek() is not None:
                    self.output_q.push(q.pop())
            self.finish_indication()
        else:
            if evt.name != f'{self.name}_start':
                self.logger.error(f'Ignoring other Events other than Clock Events {evt}')
