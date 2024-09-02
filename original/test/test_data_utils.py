import unittest

from ddt import ddt, data, unpack

from src.data_utils import data_fulfills_k_anonymity, extract_equivalence_classes, compute_equivalence_class_sizes

TEST_DATA_1 = [
    ["male", "30-60"],
    ["male", "30-60"],
    ["female", "30-60"],
    ["female", "30-60"],
]


TEST_DATA_2 = [
    # ec1, 2 elements
    [True, 5, "ANY"],
    [True, 5, "ANY"],
    # eq2, 2 elements
    [False, 5, "ANY"],
    [False, 5, "ANY"],
    # eq3, 3 elements
    [False, 8, "ANY"],
    [False, 8, "ANY"],
    [False, 8, "ANY"],
    # eq4, 4 elements
    [True, 8, "FOO"],
    [True, 8, "FOO"],
    [True, 8, "FOO"],
    [True, 8, "FOO"],
]


@ddt
class DataUtilsTestCase(unittest.TestCase):
    # Note: this test uses ddt - https://ddt.readthedocs.io/en/latest/

    @data(
        [TEST_DATA_1, [0, 1],    2, [2, 2]],
        [TEST_DATA_1, [0],       2, [2, 2]],
        [TEST_DATA_1, [1],       1, [4]],
        [TEST_DATA_2, [0, 1, 2], 4, [2, 2, 3, 4]],
        [TEST_DATA_2, [0],       2, [5, 6]],
        [TEST_DATA_2, [1],       2, [4, 7]],
        [TEST_DATA_2, [0, 1],    4, [2, 2, 3, 4]],
        [TEST_DATA_2, [1, 2],    3, [3, 4, 4]],
        [TEST_DATA_2, [0, 2],    3, [2, 4, 5]],
    )
    @unpack
    def test_extract_equivalence_classes(self, data, rel_attributes, expected_number, expected_class_sizes):
        eq_classes = extract_equivalence_classes(data, rel_attributes)
        eq_class_sizes = sorted([len(class_data) for class_data in eq_classes.values()])

        self.assertEqual(len(eq_classes), expected_number)
        # This check is dar from perfect, since it just looks at equivalence class sizes, but not the real classes :(
        self.assertEqual(eq_class_sizes, expected_class_sizes)

    @data(
        [TEST_DATA_1, [0, 1],    2, True],
        [TEST_DATA_1, [0, 1],    3, False],
        [TEST_DATA_1, [0],       2, True],
        [TEST_DATA_1, [0],       3, False],
        [TEST_DATA_1, [1],       3, True],
        [TEST_DATA_1, [1],       4, True],
        [TEST_DATA_2, [0, 1, 2], 2, True],
        [TEST_DATA_2, [0, 1, 2], 3, False],
        [TEST_DATA_2, [1, 2],    3, True],
        [TEST_DATA_2, [1, 2],    4, False],
    )
    @unpack
    def test_data_fulfills_k_anonymity(self, data, rel_attr, k, expected_result):
        self.assertEqual(data_fulfills_k_anonymity(data, rel_attr, k), expected_result)

    @data(
        [TEST_DATA_1, [0, 1],    {2: 2}],
        [TEST_DATA_1, [0],       {2: 2}],
        [TEST_DATA_1, [1],       {4: 1}],
        [TEST_DATA_2, [0, 1, 2], {2: 2, 3: 1, 4: 1}],
        [TEST_DATA_2, [0],       {5: 1, 6: 1}],
        [TEST_DATA_2, [1],       {4: 1, 7: 1}],
        [TEST_DATA_2, [2],       {4: 1, 7: 1}],
        [TEST_DATA_2, [0, 1],    {2: 2, 3: 1, 4: 1}],
        [TEST_DATA_2, [0, 2],    {2: 1, 4: 1, 5: 1}],
        [TEST_DATA_2, [1, 2],    {3: 1, 4: 2}],
    )
    @unpack
    def test_compute_equivalence_class_sizes(self, data, rel_attr, expected_dict):
        eq_class_sizes = compute_equivalence_class_sizes(data, rel_attr)

        self.assertEqual(eq_class_sizes, expected_dict)


if __name__ == '__main__':
    unittest.main()
