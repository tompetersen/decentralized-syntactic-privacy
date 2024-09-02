from typing import Tuple, List
import sys

from src.counter_information_data import NodeCounterType, CounterGroup

MOTION_LIB_PATH = "/home/tom/git/motion-fork/build/lib"
sys.path.append(MOTION_LIB_PATH)
import pandapython


PartyId = int
Host = str
Port = int


class Party:
    id: PartyId
    host: Host
    ring_port: Port  # used for ring communication
    motion_port: Port  # used for MOTION communication

    def __init__(self, id, host, ring_port, motion_port) -> None:
        super().__init__()
        self.id = id
        self.host = host
        self.ring_port = ring_port
        self.motion_port = motion_port


def result_from_sum(s: int) -> Tuple[NodeCounterType, int]:
    if s == pandapython.get_zero_mask_value():
        return NodeCounterType.Empty, 0 
    elif s == 0:
        return NodeCounterType.SmallerThanK, 0
    else:
        return NodeCounterType.Valid, s


def perform_protocol_secure_sums_gt_k(parties: List[Party], own_id: PartyId, counters: List[CounterGroup], k: int) -> List[CounterGroup]:
    """
    MOTION framework
    Secure protocol: sum(input[i]) > k

    The `counters` list items act as groups: If one item in the dict is less than k, all sums in this group are masked.

    The output of this function is quite ugly!
    - sum == 0     -> pandapython.get_zero_mask_value()
    - 0 < sum < k  -> 0
    - k <= sum     -> sum

    Example call:
    parties=[(0,"127.0.0.1",4403), (1, "127.0.0.1", 4404)]
    my_id=1
    my_inputs=[[1, 2, 3], [4, 5, 6]]
    k=5
    """
    if not counters:
        return []
    
    motion_parties = list(map(lambda p: (p.id, p.host, p.motion_port), parties))

    inputs = [list(c.items()) for c in counters]
    for i in inputs:
        i.sort(key=lambda inp: inp[0])  # sort by key for consistent input order over all boxes
    clean_inputs = [list(map(lambda inp: inp[1][1], inpu)) for inpu in inputs]
    
    print(f"MOTION: perform_protocol_secure_sums_gt_k\n\tCOUNTERS: {counters}\n\tCLEAN INPUTS: {clean_inputs}", flush=True)

    results = pandapython.perform_arithmetic_then_bool_with_groups(parties=motion_parties, my_id=own_id, my_inputs=clean_inputs, k=k)
    results = [list(map(result_from_sum, r)) for r in results]

    # map resulting (NodeCounterType, int) tuples to node_ids for each group
    motion_results = []
    for input_list, result_list in zip(inputs, results):
        motion_results.append({inp[0]: mr for inp, mr in zip(input_list, result_list)})

    return motion_results
