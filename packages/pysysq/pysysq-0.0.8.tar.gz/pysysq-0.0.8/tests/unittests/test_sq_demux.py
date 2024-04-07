import unittest
from unittest.mock import MagicMock

from pysysq.sq_base import SQTimeBase
from pysysq.sq_base.sq_clock import SQClock
from pysysq.sq_base.sq_event import SQEventManager
from pysysq.sq_base.sq_mux_demux import SQMux, SQDemux
from pysysq.sq_base.sq_mux_demux.sq_rr_mux_demux_helper import SQRRMuxDemuxHelper
from pysysq.sq_base.sq_packet import SQPacket
from pysysq.sq_base.sq_pkt_processor import SQPktProcessor
from pysysq.sq_base.sq_pkt_processor.sq_random_pkt_processing_helper import SQRandomPktProcessingHelper
from pysysq.sq_base.sq_queue import SQSingleQueue


class TestSQDemux(unittest.TestCase):

    def setUp(self):
        self.event_mgr = SQEventManager()
        self.no_of_qs = 10
        self.tx_qs = [SQSingleQueue(f'tx_q{i}', self.event_mgr, capacity=10) for i in range(self.no_of_qs)]
        self.input_q = SQSingleQueue('input_q', self.event_mgr, capacity=10)
        self.helper = SQRRMuxDemuxHelper()
        self.demux = SQDemux('mux', self.event_mgr, tx_qs=self.tx_qs, input_q=self.input_q, helper=self.helper)

        self.clk = SQClock('clk', self.event_mgr, clk_divider=1)
        self.clk.control_flow(self.demux)
        self.clk.init()
        self.demux.init()

        self.clk.start()
        self.demux.start()
        # Initialize an instance of SQObject before each test

    def run_sim_loops(self, no_of_sim_loops: int):
        for i in range(no_of_sim_loops):
            SQTimeBase.update_current_sim_time()
            self.event_mgr.run()

    def test_demux_queue_selection(self):
        # Arrange

        # push a packet to each rx queue
        for i in range(10):
            self.demux.input_q.push(SQPacket(id=i * 10))

        # Act
        self.run_sim_loops(no_of_sim_loops=11)

        # Assert
        for i in range(10):
            self.assertEqual(self.demux.tx_qs[i].pop().id, i * 10)

    def test_mux_queue_selection_with_alternate_qs_filled(self):
        # Arrange

        # push a packet to each rx queue
        for i in range(10):
            if i % 2 == 0:
                self.demux.input_q.push(SQPacket(id=i * 10))

        # Act
        self.run_sim_loops(no_of_sim_loops=11)

        # Assert
        for i in range(10):
            if i < 5:
                self.assertEqual(self.demux.tx_qs[i].pop().id, i * 20)
            else:
                self.assertEqual(self.demux.tx_qs[i].pop(), None)

