from dataclasses import dataclass
from typing import List


@dataclass
class DataFlow:
    data: str
    destination: str


@dataclass
class SQSimDataModel:
    name: str
    type: str
    comment: str
    data_flows: List[DataFlow]
    children: List["SQSimDataModel"]
    plot: bool
    sq_object_data: dict


