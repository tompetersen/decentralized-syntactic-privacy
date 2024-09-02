from secrets import randbelow
from typing import Dict, Tuple, Callable

from src.constants import AttributeIndex, GeneralizationLabel, TipsNodeId


RANDOM_UPPER_BOUND = 100000


# Contains the number of children for the resulting classes, if an attribute is specialized.
ChildCountersForAttribute = Dict[GeneralizationLabel, int]

# Contains the child counters for all attributes.
ChildCounters = Dict[AttributeIndex, ChildCountersForAttribute]

# Contains counter data (number of records, number of potential children) for one TIPS node.
TipsNodeCounter = Tuple[int, ChildCounters]

# Contains the counters for multiple TIPS nodes.
CounterInformationData = Dict[TipsNodeId, TipsNodeCounter]


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
