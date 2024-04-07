from dataclasses import dataclass
from typing import List
from ..sq_time_base import SQTimeBase


@dataclass
class SQStatisticsEntry:
    sim_time: int
    value: int
    name: str
    owner: str


class SQStatistics:
    def __init__(self):
        self._statistics: List[SQStatisticsEntry] = []

    def add(self, sq_property: str, value: int, owner: str):
        entry: SQStatisticsEntry = SQStatisticsEntry(sim_time=SQTimeBase.get_current_sim_time(),
                                                     value=value,
                                                     name=sq_property,
                                                     owner=owner)
        self._statistics.append(entry)

    def get_property(self, name, owner: str):
        return list(filter(lambda x: x.name == name and x.owner == owner, self._statistics))

    def get_all_properties(self, owner: str) -> dict:
        return {x.name: list(filter(lambda y: y.name == x.name and x.owner == owner, self._statistics)) for x in
                self._statistics}

    def get_all_property_names(self, owner: str):
        return list(set([x.name for x in self._statistics if x.owner == owner]))
