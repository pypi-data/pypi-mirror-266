import unittest
from unittest.mock import MagicMock

from pysysq.sq_base import SQTimeBase
from pysysq.sq_base.sq_clock import SQClock
from pysysq.sq_base.sq_event import SQEventManager
from pysysq.sq_base.sq_packet import SQPacket
from pysysq.sq_base.sq_pkt_processor import SQPktProcessor
from pysysq.sq_base.sq_pkt_processor.sq_random_pkt_processing_helper import SQRandomPktProcessingHelper
from pysysq.sq_base.sq_queue import SQSingleQueue


class TestSQPacketProcessor(unittest.TestCase):
    def setUp(self):
        self.event_mgr = SQEventManager()
        # Initialize an instance of SQObject before each test
        self.clk = SQClock('clk', self.event_mgr, clk_divider=1)
        self.input_q1 = SQSingleQueue('input_q1', self.event_mgr, capacity=10)
        self.input_q2 = SQSingleQueue('input_q2', self.event_mgr, capacity=10)
        self.helper = SQRandomPktProcessingHelper()

        self.helper2 = SQRandomPktProcessingHelper()

        self.producer = SQPktProcessor('producer', self.event_mgr, clk=self.clk, input_q=self.input_q1,
                                       helper=self.helper)
        self.clk.init()
        self.producer.init()
        # self.consumer = SQPktProcessor('consumer', self.event_mgr, clk=self.clk, input_q=self.input_q2,
        #                                helper=self.helper2)

        # self.helper2.set_owner(self.consumer)
        self.helper.set_owner(self.producer)

    def run_sim_loops(self, no_of_sim_loops: int):
        for i in range(no_of_sim_loops):
            SQTimeBase.update_current_sim_time()
            self.event_mgr.run()

    def test_process_packet(self):
        # Arrange
        self.clk.start()
        self.producer.start()
        self.producer.input_queue.push(SQPacket())
        self.producer.finish_indication = MagicMock()
        self.helper.get_processing_ticks = MagicMock(return_value=3)
        self.helper.process_packet = MagicMock()
        states = ['IDLE', 'PROCESSING', 'COMPLETE', 'IDLE']
        # Act
        for i in range(4):
            self.run_sim_loops(no_of_sim_loops=1)
            print(self.producer._state)
            self.assertEqual(self.producer._state.get_state_name(), states[i])
        self.assertEqual(self.helper.process_packet.call_count, 3)

    def test_process_with_large_processing_time(self):
        self.clk.start()
        self.producer.start()
        self.producer.input_queue.push(SQPacket())
        self.producer.finish_indication = MagicMock()
        self.helper.get_processing_ticks = MagicMock(return_value=30)
        self.helper.process_packet = MagicMock()

        # Act
        for i in range(31):
            self.run_sim_loops(no_of_sim_loops=1)
        self.assertEqual(self.helper.process_packet.call_count, 30)
