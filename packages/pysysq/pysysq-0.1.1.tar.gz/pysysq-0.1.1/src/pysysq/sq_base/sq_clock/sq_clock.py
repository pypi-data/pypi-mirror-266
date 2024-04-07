from ..sq_object import SQObject
from ..sq_logger import SQLogger
from ..sq_event import SQEvent
from ..sq_event.sq_event_manager import SQEventManager
from ..sq_time_base import SQTimeBase


class SQClock(SQObject):
    """
    A Clock object that ticks at a given frequency based on the clk_divider
    """

    def __init__(self, data: dict[str, any]):
        super().__init__(data)
        self.logger = SQLogger(self.__class__.__name__, self.name)
        self.clk_divider = data.get('clk_divider', 1)
        self.is_self_ticking = True

    def process_packet(self, evt: SQEvent):
        current_sim_time = SQTimeBase.get_current_sim_time()
        # only tick if the current sim time is a multiple of clk_divider
        if current_sim_time % self.clk_divider == 0:
            self.tick += 1
            self.logger.info(
                f" Clock Tick = {self.tick} on sim time {current_sim_time}")
            self.finish_indication()
        else:
            self.logger.debug(
                f" Skipping at Clock Tick = {self.tick} on sim time {current_sim_time}")
        super().process_packet(evt)
