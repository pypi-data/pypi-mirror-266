from typing import Callable, Dict

from .sq_sim_data_model import SQSimDataModel


class SQCodeGenModel:
    def __init__(self, data: SQSimDataModel) -> None:
        self.model = data
        self.imports = ['from pysysq import *']
        self.queues = []
        self.clocks = []
        self.sim_objects = []
        self.simulator = None
        self.plugins = []
        self.plot_objects = []
        self.name = ""
        self.parser: Dict[str, Callable[[SQSimDataModel], None]] = {
            'SQSimulator': self._parse_simulator,
            'SQQueue': self._parse_queues,
            'SQClock': self._parse_clocks,
            'SQFilter': self._parse_sim_object,
            'SQMerger': self._parse_sim_object,
            'SQMux': self._parse_sim_object,
            'SQDemux': self._parse_sim_object,
            'SQPacketGenerator': self._parse_sim_object,
            'SQPktProcessor': self._parse_sim_object,
            'SQPktSink': self._parse_sim_object,
            'SQSplitter': self._parse_sim_object
        }
        self._parse_simulator(self.model)

    def _parse_simulator(self, data: SQSimDataModel) -> None:
        for child in data.children:
            self.parser[child.type](data=child)
        self.simulator = data
        self.name = self.simulator.sq_object_data['name']

    def _parse_queues(self, data: SQSimDataModel) -> None:
        self.queues.append(data)
        if data.plot:
            self.plot_objects.append(data.name)

    def _parse_clocks(self, data: SQSimDataModel) -> None:
        self.clocks.append(data)
        if data.plot:
            self.plot_objects.append(data.name)

    def _parse_sim_object(self, data: SQSimDataModel) -> None:
        self.sim_objects.append(data)
        if data.plot:
            self.plot_objects.append(data.name)

    def generate_params(self, data: Dict[str, str]) -> str:
        ret_val = ', '.join([f'{k}={v}' for k, v in data.items()])
        return ret_val
