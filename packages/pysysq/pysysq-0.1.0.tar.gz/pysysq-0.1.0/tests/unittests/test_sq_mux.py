import unittest
from unittest.mock import MagicMock

from pysysq.sq_base import SQTimeBase
from pysysq.sq_base.sq_clock import SQClock
from pysysq.sq_base.sq_event import SQEventManager
from pysysq.sq_base.sq_mux_demux import SQMux
from pysysq.sq_base.sq_mux_demux.sq_rr_mux_demux_helper import SQRRMuxDemuxHelper
from pysysq.sq_base.sq_packet import SQPacket
from pysysq.sq_base.sq_pkt_processor import SQPktProcessor
from pysysq.sq_base.sq_pkt_processor.sq_random_pkt_processing_helper import SQRandomPktProcessingHelper
from pysysq.sq_base.sq_queue import SQSingleQueue


class TestSQMux(unittest.TestCase):

    def setUp(self):
        self.event_mgr = SQEventManager()
        self.no_of_qs = 10
        self.rx_qs = [SQSingleQueue(f'rx_q{i}', self.event_mgr, capacity=10) for i in range(self.no_of_qs)]
        self.output_q = SQSingleQueue('output_q', self.event_mgr, capacity=10)
        self.helper = SQRRMuxDemuxHelper()
        self.mux = SQMux('mux', self.event_mgr, rx_rqs=self.rx_qs, output_q=self.output_q, helper=self.helper)

        self.clk = SQClock('clk', self.event_mgr, clk_divider=1)
        self.clk.control_flow(self.mux)
        self.clk.init()
        self.mux.init()

        self.clk.start()
        self.mux.start()
        # Initialize an instance of SQObject before each test

    def run_sim_loops(self, no_of_sim_loops: int):
        for i in range(no_of_sim_loops):
            SQTimeBase.update_current_sim_time()
            self.event_mgr.run()

    def test_mux_queue_selection(self):
        # Arrange

        # push a packet to each rx queue
        for i in range(10):
            self.mux.rx_qs[i].push(SQPacket(id=i * 10))

        # Act
        self.run_sim_loops(no_of_sim_loops=11)

        # Assert
        for i in range(10):
            self.assertEqual(self.mux.output_q.pop().id, i * 10)

    def test_mux_queue_selection_with_alternate_qs_filled(self):
        # Arrange

        # push a packet to each rx queue
        for i in range(10):
            if i % 2 == 0:
                self.mux.rx_qs[i].push(SQPacket(id=i * 10))

        # Act
        self.run_sim_loops(no_of_sim_loops=11)

        # Assert
        for i in range(10):
            if i < 5:
                self.assertEqual(self.mux.output_q.pop().id, i * 20)
            else:
                self.assertEqual(self.mux.output_q.pop(), None)

