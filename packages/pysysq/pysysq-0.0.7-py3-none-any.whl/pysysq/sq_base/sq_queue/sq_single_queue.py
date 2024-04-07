from typing import List, Union
from ..sq_logger import SQLogger
from ..sq_queue import SQQueue
from ..sq_packet import SQPacket
from ..sq_event import SQEvent


class SQSingleQueue(SQQueue):
    def push(self, pkt: SQPacket):
        super().push(pkt)
        if len(self.queue) < self.capacity:
            self.queue.append(pkt)
            self.logger.info(f'Packet Queued {pkt}')
            self.pending_pkt_count = len(self.queue)
            self.total_enqueued_pkt_count += 1
            self.finish_indication()
        else:
            self.logger.warning(f' Queue Full , Dropping Packet {pkt}')
            self.pending_pkt_count = len(self.queue)
            self.dropped_pkt_count += 1

    def peek(self):
        if len(self.queue) == 0:
            return None
        return self.queue[0]

    def is_empty(self) -> bool:
        return len(self.queue) == 0

    def __init__(self, data: dict[str, any]):
        super().__init__(data)
        self.queue: List[SQPacket] = []
        self.capacity = data.get('capacity', 10)
        self.logger = SQLogger(self.__class__.__name__, self.name)
        self.dropped_pkt_count = 0
        self.pending_pkt_count = 0
        self.total_enqueued_pkt_count = 0
        self.register_property('dropped_pkt_count')
        self.register_property('pending_pkt_count')
        self.register_property('total_enqueued_pkt_count')

    def pop(self, **kwargs) -> Union[SQPacket, None]:
        super().pop()
        if len(self.queue) == 0:
            return None
        return self.queue.pop(0)

    def process_packet(self, evt: SQEvent):
        super().process_packet(evt)
        if evt.owner is not self:
            self.push(evt.data)
        else:
            if evt.name != f'{self.name}_start':
                self.logger.error(f'Ignoring Self Event {evt}')
