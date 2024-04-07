from dataclasses import dataclass
from typing import Any


@dataclass
class SQMetadata:
    owner: str
    name: str
    value: Any
