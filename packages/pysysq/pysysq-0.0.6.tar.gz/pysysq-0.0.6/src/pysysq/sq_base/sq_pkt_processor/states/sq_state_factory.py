from typing import Union
from .sq_pkt_processor_state import SQPktProcState
from .sq_pkt_proc_idle import SQPktProcStateIdle
from .sq_pkt_proc_processing import SQPktProcStateProcessing
from .sq_pkt_proc_complete import SQPktProcStateComplete


class SQStateFactory:

    def create_state(self, name: str, owner) -> Union[SQPktProcState, None]:
        state = None
        if name == "IDLE":
            state = SQPktProcStateIdle(owner=owner, factory=self)
        elif name == "PROCESSING":
            state = SQPktProcStateProcessing(owner=owner, factory=self)
        elif name == "COMPLETE":
            state = SQPktProcStateComplete(owner=owner, factory=self)
        else:
            state = None
        return state
