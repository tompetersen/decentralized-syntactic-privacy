import csv
import itertools
from collections import defaultdict, Counter
from typing import List, Dict, Tuple

from src.constants import AttributeIndex, Data


def read_csv_data(data_path: str, delimiter: str = ',', missing_value: str = '?') -> Tuple[List[str], Data]:
    """
    Read data from a csv file (separated by comma).

    :param data_path: the file path
    :param delimiter: the csv file data delimiter
    :param missing_value: rows with fields being set to this value are not incorporated (to remove incomplete data rows)

    :return: the read data
    """
    with open(data_path, newline='') as csvfile:
        data_read = []
        all_data = csv.reader(csvfile, delimiter=delimiter, quotechar='|')
        categories = all_data.__next__()
        for row in itertools.islice(all_data, 1, None):
            if missing_value not in row and len(row) > 0:  # remove missing value rows
                data_read.append([_parse_data_point(data_point) for data_point in row])
    return categories, data_read


def _parse_data_point(data_point):
    my_value = str(data_point)
    try:
        my_value = int(data_point)
    except ValueError:
        try:
            my_value = float(data_point)
        except ValueError:
            pass
            # happens quite frequently, for missing values in some categories
            # print('Could not read data_point, replacing it by 0: ' + data_point)
    return my_value


def extract_equivalence_classes(data: Data, relevant_attribute_indices: List[AttributeIndex]) -> Dict[str, Data]:
    """
    Compute the equivalence classes (meaning the data rows with the same attribute values w.r.t. some attribute indices) in a data set.

    :param data: the data
    :param relevant_attribute_indices: the attribute indices
    :return: the equivalence classes grouped by the equivalence class key, e.g., "1:f|2:30-60|"
    """
    result = defaultdict(list)

    for row in data:
        ra_key = "".join([str(ai) + ":" + str(row[ai]) + "|" for ai in relevant_attribute_indices])
        result[ra_key].append(row)

    return result


def data_fulfills_k_anonymity(data: Data, relevant_attribute_indices: List[AttributeIndex], k: int) -> bool:
    """
    Check, if a data set fulfills k-anonymity w.r.t. given attributes (QIDs).

    :param data: the data
    :param relevant_attribute_indices: the attribute indices
    :param k: the anonymity parameter
    :return: True, if k-anonymity is fulfilled, False otherwise
    """
    equiv_classes = extract_equivalence_classes(data, relevant_attribute_indices)
    return all([len(c) >= k for c in equiv_classes.values()])


def compute_equivalence_class_sizes(data: Data, relevant_attribute_indices: List[AttributeIndex]) -> Counter:
    """
    Returns the distribution of equivalence class sizes w.r.t. given attributes in the data.

    :param data: the data
    :param relevant_attribute_indices: the attribute indices
    :return: a counter containing the number of equivalence classes per size
    """
    equiv_classes = extract_equivalence_classes(data, relevant_attribute_indices)

    return Counter([len(ec) for ec in equiv_classes.values()])
