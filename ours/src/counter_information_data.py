from enum import Enum
from secrets import randbelow
from typing import Dict, Tuple, Callable, List

from src.constants import AttributeIndex, GeneralizationLabel, TipsNodeId

RANDOM_UPPER_BOUND = 100000


class NodeCounterType(Enum):
    DataContent = 0  # used in boxes without "global" view
    Undefined = 1
    Empty = 2
    SmallerThanK = 3
    Valid = 4


NodeCounterInfo = Tuple[NodeCounterType, int]

# Contains the number of children for the resulting classes, if an attribute is specialized.
ChildCountersForAttribute = Dict[GeneralizationLabel, NodeCounterInfo]

# Contains the child counters for all attributes.
ChildCounters = Dict[AttributeIndex, ChildCountersForAttribute]

# Contains counter data (number of records, number of potential children) for one TIPS node.
TipsNodeCounter = Tuple[NodeCounterInfo, ChildCounters]

# Contains the counters for multiple TIPS nodes.
CounterInformationData = Dict[TipsNodeId, TipsNodeCounter]

# Contains related tips node counters (e.g., all child counters for one specialization)
CounterGroup = Dict[TipsNodeId, NodeCounterInfo]


def substract_counter_information_data(counter_data: CounterInformationData, counter_data_to_substract: CounterInformationData) -> CounterInformationData:
    """
    Substract counter data (number of records as well as all child counters) C1 - C2.
    This is used for deobfuscating counters during the secure sum protocol.

    :param counter_data: the counter C1
    :param counter_data_to_substract: the counter C2
    :return: the resulting counter C1 - C2
    """
    def substract(a, b):
        return a - b
    return _combine_counter_information_data_with_operator(counter_data, counter_data_to_substract, substract)


def add_counter_information_data(counter_data1: CounterInformationData, counter_data2: CounterInformationData) -> CounterInformationData:
    """
    Add counter data (number of records as well as all child counters) C1 + C2.
    This is used for obfuscating counters during the secure sum protocol.

    :param counter_data1: the counter C1
    :param counter_data2: the counter C2
    :return: the resulting counter C1 + C2
    """
    def add(a, b):
        return a + b

    return _combine_counter_information_data_with_operator(counter_data1, counter_data2, add)


def _combine_counter_information_data_with_operator(counter_data1: CounterInformationData, counter_data2: CounterInformationData, operator: Callable[[int, int], int]) -> CounterInformationData:
    result: CounterInformationData = {}

    for node_id in set(list(counter_data1.keys()) + list(counter_data2.keys())):
        node_counter_sum = _combine_counters_with_operator(counter_data1[node_id], counter_data2[node_id], operator)
        result[node_id] = node_counter_sum

    return result


def _combine_counters_with_operator(counter1: TipsNodeCounter, counter2: TipsNodeCounter, operator: Callable[[int, int], int]) -> TipsNodeCounter:
    number_of_records = operator(counter1[0], counter2[0])

    child_counters_result: ChildCounters = {}
    for attr_index in set(list(counter1[1].keys()) + list(counter2[1].keys())):
        child_counters_for_attribute_result: ChildCountersForAttribute = {}
        for gen_label in set(list(counter1[1][attr_index].keys()) + list(counter2[1][attr_index].keys())):
            child_counter = operator(counter1[1][attr_index][gen_label], counter2[1][attr_index][gen_label])
            child_counters_for_attribute_result[gen_label] = child_counter
        child_counters_result[attr_index] = child_counters_for_attribute_result

    return number_of_records, child_counters_result


def counter_information_data_with_random_numbers(counter_data: CounterInformationData) -> CounterInformationData:
    """
    Generate counter information data filled with random numbers using the structure of existing counter information data.

    :param counter_data: the counter used as template
    :return: the randomized counter information data
    """
    result: CounterInformationData = {}

    for node_id in counter_data:
        child_counters_result: ChildCounters = {}
        for attr_index in counter_data[node_id][1]:
            child_counters_for_attribute_result: ChildCountersForAttribute = {}
            for gen_label in counter_data[node_id][1][attr_index]:
                random_child_counter = randbelow(RANDOM_UPPER_BOUND)
                child_counters_for_attribute_result[gen_label] = random_child_counter
            child_counters_result[attr_index] = child_counters_for_attribute_result
        random_nr_of_records = randbelow(RANDOM_UPPER_BOUND)
        result[node_id] = random_nr_of_records, child_counters_result

    return result


def counter_groups_from_counter_information_data(data: CounterInformationData, only_undefined: bool = False) -> List[CounterGroup]:
    """
    Construct groups [{node_counter}, {child_counters 1}, ..., {child_counters n}] of undefined counters from counter information data.
    :param data: the counter information data to be grouped
    :param only_undefined: if set, return only undefined counters
    """
    result = []

    for node_id, node_counter in data.items():
        if not only_undefined or node_counter[0][0] == NodeCounterType.Undefined:
            result.append({node_id: node_counter[0]})
        for child_counters in node_counter[1].values():
            if only_undefined:
                undefined_child_counters = {k: v for k, v in child_counters.items() if v[0] == NodeCounterType.Undefined}
                if undefined_child_counters:
                    result.append(undefined_child_counters)
            else:
                result.append(child_counters)

    return result


def node_ids_from_counter_groups(counter_groups: List[CounterGroup]) -> List[TipsNodeId]:
    """
    Extract all TipNodeIds from a list of CounterGroups.
    """
    ids = [g.keys() for g in counter_groups]
    return [id for sublist in ids for id in sublist]


def filter_counter_groups_by_id(counter_groups: List[CounterGroup], relevant_ids: List[TipsNodeId]) -> List[CounterGroup]:
    """
    Filter all CounterGroup members by "TipsNodeId in relevant_ids".
    """
    result = []
    for g in counter_groups:
        relevant_nodes = {k: v for k, v in g.items() if k in relevant_ids}
        if relevant_nodes:
            result.append(relevant_nodes)
    return result


def incorporate_counter_groups(data: CounterInformationData, counter_groups: List[CounterGroup]) -> CounterInformationData:
    """
    TODO
    """
    flat_counters = {k: v for g in counter_groups for k, v in g.items()}
    result = {}

    for node_id, node_counter in data.items():
        # incorporate node counter
        new_node_counter = node_counter[0]
        if node_id in flat_counters:
            new_node_counter = flat_counters[node_id]

        # incorporate child counters
        new_child_counters = {}
        for attr_index, child_counters in node_counter[1].items():
            new_child_counters[attr_index] = {child_id: (flat_counters[child_id] if child_id in flat_counters else child_counters[child_id]) for child_id in child_counters}

        # create result tuple
        result[node_id] = (new_node_counter, new_child_counters)

    return result
