from dataclasses import dataclass


@dataclass
class SQPacketInfo:
    no_of_pkts: int
    pkt_sizes: [int]
    pkt_classes: [str]
    pkt_priorities: [int]
