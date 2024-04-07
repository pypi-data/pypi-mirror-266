from .sq_generator_state import SQPktGeneratorState
from ...sq_event import SQEvent


class SQPktGeneratorQueuingState(SQPktGeneratorState):
    def process_packet(self, evt: SQEvent):
        if len(self.owner.packets)>0:
            self.owner.output_q.push(self.owner.packets[self.owner.tick])
            self.owner.generated_pkts += 1
            self.owner.total_pkts += 1
            self.owner.logger.info(f'Packet {self.owner.packets[self.owner.tick]} Ready for Queuing')
            self.owner.tick += 1
        if self.owner.tick >= len(self.owner.packets):
            self.owner.packets = []
            self.owner.tick = 0
            self.owner.set_state(self.factory.create_state(name='GENERATING', owner=self.owner))
        self.owner.finish_indication()

    def get_state_name(self):
        return f'QUEUING'
