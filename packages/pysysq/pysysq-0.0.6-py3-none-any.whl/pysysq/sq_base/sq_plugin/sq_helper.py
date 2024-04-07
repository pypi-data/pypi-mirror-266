from typing import Generator, List, Union

from abc import abstractmethod
from ..sq_packet import SQPacket, SQMetadata

from ..sq_event import SQEvent


class SQHelper:

    def __init__(self, data: dict[str, any]):
        self.owner = data.get('owner', None)
        self.data = data

    def set_owner(self, owner):
        self.owner = owner

    @abstractmethod
    def generate_packets(self) -> Generator[List[SQPacket], None, None]:
        pass

    @abstractmethod
    def get_processing_cycles(self, pkt: SQPacket) -> int:
        pass

    @abstractmethod
    def process_packet(self, pkt: SQPacket, tick: int) -> Union[SQMetadata, None]:
        pass

    @abstractmethod
    def filter_packet(self, pkt: SQPacket) -> bool:
        pass

    @abstractmethod
    def process_data(self, data: SQEvent, tick: int):
        pass

    @abstractmethod
    def select_input_queue(self) :
        pass

    @abstractmethod
    def select_output_queue(self, pkt):
        pass
