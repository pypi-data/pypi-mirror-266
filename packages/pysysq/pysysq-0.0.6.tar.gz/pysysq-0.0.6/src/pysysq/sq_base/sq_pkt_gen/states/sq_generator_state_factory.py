from typing import Union
from .sq_generator_state import SQPktGeneratorState
from .sq_pkt_generator_gen_state import SQPktGeneratorGenState
from .sq_pkt_generator_queuing_state import SQPktGeneratorQueuingState


class SQGeneratorStateFactory:
    def create_state(self, name: str, owner) -> Union[SQPktGeneratorState, None]:
        state = None
        if name == "GENERATING":
            state = SQPktGeneratorGenState(owner=owner, factory=self)
        elif name == "QUEUING":
            state = SQPktGeneratorQueuingState(owner=owner, factory=self)
        else:
            state = None
        return state
