from src.counter_information_data import TipsNodeCounter
from src.qid_hierarchy_node import NumericalQidHierarchyNode


def get_test_data():
    return [
        [1, 92, 2, 3.0, 18.0, 0, 0, 1.0, 0.0, 0.0, 0.0, 1, 0, 8.0, 1.0, 3.0, -1, 6.0, 1.0, 6.0],
        [1, 87, 2, 0.0, 14.0, 0, 0, 1.0, 0.0, 1.0, 0.0, 0, 1, 7.0, 1.0, 4.0, 5.0, 1.0, 0.0, 0.0],
        [1, 72, 1, 0.0, 16.0, 0, 0, 1.0, 0.0, 0.0, 1.0, 0, 1, -1, 1.0, 4.0, 7.0, 3.0, 0.0, 0.0],
        [1, 77, 2, 0.0, 16.0, 0, 0, 0.0, 0.0, 1.0, 0.0, 0, 1, 10.0, 1.0, 3.0, 1.0, 2.0, 0.0, 2.0],
        [1, 85, 2, 2.0, 19.0, 0, 1, 1.0, 0.0, 1.0, 0.0, 1, 0, 8.0, 0.0, 4.0, 6.0, 4.0, 0.0, 4.0],
        [1, 88, 2, 3.0, 16.0, 0, 1, 1.0, 1.0, 1.0, 0.0, 1, 0, -1, 0.0, 3.0, 7.0, 4.0, 0.0, 6.0],
        [1, 66, 1, 0.0, 12.0, 1, 0, 1.0, 0.0, 0.0, 1.0, 0, 1, -1, 1.0, 4.0, 7.0, 3.0, 0.0, 0.0],
        [1, 52, 2, 0.0, 14.0, 0, 0, 1.0, 0.0, 0.0, 1.0, 0, 1, -1, 1.0, 4.0, 7.0, 3.0, 0.0, 0.0],
        [1, 68, 2, 1.0, 12.0, 1, 0, 1.0, 0.0, 0.0, 1.0, 0, 1, -1, 1.0, 4.0, 7.0, 3.0, 0.0, 0.0],
        [1, 75, 1, 2.0, 16.0, 0, 0, 1.0, 0.0, 0.0, 1.0, 0, 1, -1, 1.0, 4.0, 7.0, 3.0, 0.0, 0.0],
    ]


def get_test_age_tree() -> NumericalQidHierarchyNode:
    age_root = NumericalQidHierarchyNode(min=1, max=119)
    age_0 = NumericalQidHierarchyNode(parent=age_root, min=1, max=76)
    age_0_0 = NumericalQidHierarchyNode(parent=age_0, min=1, max=65)
    age_0_1 = NumericalQidHierarchyNode(parent=age_0, min=66, max=76)
    age_1 = NumericalQidHierarchyNode(parent=age_root, min=77, max=119)
    age_1_0 = NumericalQidHierarchyNode(parent=age_1, min=77, max=82)
    age_1_1 = NumericalQidHierarchyNode(parent=age_1, min=83, max=119)
    return age_root


def get_test_sex_tree() -> NumericalQidHierarchyNode:
    sex_root = NumericalQidHierarchyNode(min=1, max=2)
    sex_0 = NumericalQidHierarchyNode(parent=sex_root, min=1, max=1)
    sex_1 = NumericalQidHierarchyNode(parent=sex_root, min=2, max=2)
    return sex_root


def get_test_attribute_trees():
    return {
        1: get_test_age_tree(),
        2: get_test_sex_tree()
    }


def get_test_counters1() -> TipsNodeCounter:
    return 9, {
        1:
            {
                '0-77': 2,
                '76-120': 7
            },
        2:
            {
                '1': 3,
                '2': 6
            },
        3:
            {
                '0.0': 7,
                '2.0': 0,
                '3.0': 2
            }
    }


def get_test_counters2():
    return 15, {
        1:
            {
                '0-77': 4,
                '76-120': 11
            },
        2:
            {
                '1': 7,
                '2': 8
            },
        3:
            {
                '0.0': 10,
                '2.0': 3,
                '3.0': 2
            }
    }
