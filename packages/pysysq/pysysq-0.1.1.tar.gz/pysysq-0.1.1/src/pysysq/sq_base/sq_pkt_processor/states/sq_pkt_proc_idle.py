from .sq_pkt_processor_state import SQPktProcState
from ...sq_event import SQEvent


class SQPktProcStateIdle(SQPktProcState):

    def process_packet(self, evt: SQEvent):
        self.owner.curr_pkt = self.owner.input_queue.pop()
        self.owner.start_tick = self.owner.tick
        if self.owner.curr_pkt is None:
            self.owner.logger.info(f'{self.owner.name} No Packet to Process')
        else:
            self.owner.pkt_size_sum += self.owner.curr_pkt.size
            self.owner.pkt_size_average = self.owner.pkt_size_sum / (self.owner.no_of_processed_pkts + 1)
            self.owner.processing_time = self.owner.helper.get_processing_cycles(self.owner.curr_pkt)
            metadata = self.owner.helper.process_packet(self.owner.curr_pkt, self.owner.tick)
            self.owner.update_progress()
            if metadata is not None:
                self.owner.data_indication(data=metadata)

            self.owner.logger.info(f'{self.owner.name} Start Processing Packet '
                                   f'{self.owner.curr_pkt} Expected processing time '
                                   f'{self.owner.processing_time} current Tick {self.owner.tick}')
            self.owner.set_state(self.factory.create_state('PROCESSING', owner=self.owner))

    def get_state_name(self):
        return f'IDLE'
