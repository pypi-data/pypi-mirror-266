from abc import ABC, abstractmethod

from ...sq_event import SQEvent


class SQPktGeneratorState(ABC):
    def __init__(self, owner, factory):
        self.owner = owner
        self.factory = factory

    @abstractmethod
    def process_packet(self, evt: SQEvent):
        pass

    @abstractmethod
    def get_state_name(self):
        pass

    def __repr__(self):
        return f'{self.get_state_name()}'
