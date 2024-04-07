from dataclasses import dataclass, field
from typing import List


@dataclass
class SQPacket:
    id: int = 0
    size: int = 0
    priority: int = 0
    class_name: str = ""
    src: str = ""
    destination: str = ""
    generation_time: int = 0
    termination_time: int = 0
    path: List[str] = field(default_factory=list)
