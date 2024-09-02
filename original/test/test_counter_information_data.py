import unittest

from src.counter_information_data import _combine_counters_with_operator, \
    counter_information_data_with_random_numbers, CounterInformationData, add_counter_information_data, \
    substract_counter_information_data
from src.tips_nodes import TipsNode
from test.testdata import get_test_counters1, get_test_counters2, get_test_attribute_trees


class CounterInformationDataTest(unittest.TestCase):

    def setUp(self) -> None:
        self.tips_node = TipsNode([], get_test_attribute_trees())

    def test_combine_counters_with_operator(self):
        # arrange
        counter1 = get_test_counters1()
        counter2 = get_test_counters2()

        # act
        number_of_records, child_counters_result = _combine_counters_with_operator(counter1, counter2, lambda a,b: a+b)

        # assert
        self.assertEqual(number_of_records, counter1[0] + counter2[0])
        self.assertEqual(child_counters_result[1]['0-77'], counter1[1][1]['0-77'] + counter2[1][1]['0-77'])

    def test_counter_information_data_with_random_numbers(self):
        # arrange
        tips_counter = self.tips_node.extract_counter()
        counter_data = {self.tips_node.id: tips_counter}

        # act
        random_counters: CounterInformationData = counter_information_data_with_random_numbers(counter_data)

        # assert
        self.assertEqual(tips_counter[0], 0)
        self.assertEqual(tips_counter[1][1]['1:76'], 0)
        self.assertGreater(random_counters[self.tips_node.id][0], 0)
        self.assertGreater(random_counters[self.tips_node.id][1][1]['1:76'], 0)

    def test_add_counter_information_data(self):
        # arrange
        tips_counter = self.tips_node.extract_counter()
        counter_data = {self.tips_node.id: tips_counter}
        random_counters1: CounterInformationData = counter_information_data_with_random_numbers(counter_data)
        random_counters2: CounterInformationData = counter_information_data_with_random_numbers(counter_data)

        # act
        result = add_counter_information_data(random_counters1, random_counters2)

        # assert
        self.assertEqual(result[self.tips_node.id][0], random_counters1[self.tips_node.id][0] + random_counters2[self.tips_node.id][0])
        self.assertEqual(result[self.tips_node.id][1][1]['1:76'], random_counters1[self.tips_node.id][1][1]['1:76'] + random_counters2[self.tips_node.id][1][1]['1:76'])

    def test_substract_counter_information_data(self):
        # arrange
        tips_counter = self.tips_node.extract_counter()
        counter_data = {self.tips_node.id: tips_counter}
        random_counters: CounterInformationData = counter_information_data_with_random_numbers(counter_data)

        # act
        result = substract_counter_information_data(random_counters, counter_data)

        # assert
        self.assertEqual(result[self.tips_node.id][0], random_counters[self.tips_node.id][0])
        self.assertEqual(result[self.tips_node.id][1][1]['1:76'], random_counters[self.tips_node.id][1][1]['1:76'])


if __name__ == '__main__':
    unittest.main()
