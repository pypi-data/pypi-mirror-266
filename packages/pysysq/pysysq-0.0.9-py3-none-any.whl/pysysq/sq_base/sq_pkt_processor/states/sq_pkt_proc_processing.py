from .sq_pkt_processor_state import SQPktProcState
from ...sq_event import SQEvent


class SQPktProcStateProcessing(SQPktProcState):
    def process_packet(self, evt: SQEvent):
        metadata = self.owner.helper.process_packet(self.owner.curr_pkt, self.owner.tick)
        if metadata is not None:
            self.owner.data_indication(data=metadata)
        self.owner.update_progress()
        self.owner.logger.info(f'{self.owner.name} Continue Processing Packet '
                               f'{self.owner.curr_pkt} Time {self.owner.tick}')
        if self.owner.tick - self.owner.start_tick >= self.owner.processing_time - 2:
            self.owner.set_state(self.factory.create_state('COMPLETE', owner=self.owner))

    def get_state_name(self):
        return f'PROCESSING'
