from typing import Union

from ..sq_object import SQObject
from ..sq_event import SQEventManager, SQEvent
from ..sq_logger import SQLogger
from .states import SQPktGeneratorState
from ..sq_queue import SQQueue
from ..sq_clock import SQClock
from .states import SQGeneratorStateFactory
from ..sq_plugin import SQHelper


class SQPacketGenerator(SQObject):
    """
    Base class for all Packet Generators in the simulation
    The class implements the basic functionality of a packet generator
    """

    def __init__(self, data: dict[str, any]):

        super().__init__(data)
        self.logger = SQLogger(self.__class__.__name__, self.name)
        factory = SQGeneratorStateFactory()
        self.state: SQPktGeneratorState = factory.create_state("GENERATING", self)
        self.generated_pkts = 0
        self.total_pkts = 0
        self.output_q = data.get('output_q', None)
        if self.output_q is None:
            raise ValueError('output_q should be provided')
        self.clk = data.get('clk', None)
        if self.clk is not None:
            self.clk.control_flow(self)
        else:
            raise ValueError('Clock not provided')
        if self.helper is None:
            raise ValueError('Helper not provided')

        self.register_property('generated_pkts')
        self.register_property('total_pkts')
        self.packets = []

    def set_state(self, state):
        self.state = state

    def process_packet(self, evt: SQEvent):
        super().process_packet(evt)
        if evt.owner is self.clk:
            self.state.process_packet(evt)
        else:
            if evt.name != f'{self.name}_start':
                self.logger.error(f'Ignoring Events other than Clock Events {evt}')
