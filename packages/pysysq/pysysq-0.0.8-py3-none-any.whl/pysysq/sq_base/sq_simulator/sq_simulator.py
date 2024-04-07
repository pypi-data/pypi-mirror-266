import time
from ..sq_object import SQObject
from ..sq_event import SQEvent
from ..sq_event import SQEventManager
from ..sq_logger import SQLogger
from ..sq_time_base import SQTimeBase


class SQSimulator(SQObject):

    def start(self):
        super().start()
        self.process_packet(self.start_evt)

    def process_packet(self, evt: SQEvent):
        while SQTimeBase.get_current_sim_time() < self.max_sim_time:
            self.event_manager.run()
            SQTimeBase.update_current_sim_time()
            self.tick += 1
            self.logger.debug(f'Simulator Tick {self.tick}')
            time.sleep(self.time_step)
        self.event_manager.run()
        self.deinit()

    def __init__(self, data: dict[str, any]):
        """
        Constructor for the SQSimulator
        :param name: Name of the Simulator
        :param event_mgr: Event Manager to be used
        :param kwargs: Optional parameters
            max_sim_time: Maximum Simulation Time
            time_step: Time Step (in seconds)
        """
        super().__init__(data)
        SQTimeBase.reset_current_sim_time()
        self.max_sim_time: int = data.get('max_sim_time', 100)
        self.time_step: float = data.get('time_step', 0.1)
        self.logger = SQLogger(self.__class__.__name__, self.name)
        self.self_starting = True
