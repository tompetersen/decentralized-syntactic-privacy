import unittest
from typing import List

from src.constants import Data
from src.counter_information_data import ChildCounters, TipsNodeCounter, CounterInformationData
from src.tips_nodes import setup_tips_leaf_nodes, setup_tips_root_node, TipsNode, \
    extract_counter_information_data_from_tips_nodes, get_anonymous_result_data, perform_refinements
from test.testdata import get_test_data, get_test_counters1, get_test_attribute_trees


class TipsNodesTest(unittest.TestCase):
    TEST_K = 5

    def setUp(self) -> None:
        self.raw_test_data = get_test_data()
        self.qid_attributes = get_test_attribute_trees()
        self.tips_counters1 = get_test_counters1()

    def test_setup_without_data_yields_zero_counters(self):
        # act
        tips_node = self.zero_node()
        childcounters: ChildCounters = tips_node.get_child_counters()

        # assert
        self.assertEqual(tips_node.number_of_records, 0)
        for attr_index in childcounters:
            for gen_label in childcounters[attr_index]:
                self.assertEqual(childcounters[attr_index][gen_label], 0)

    def zero_node(self):
        tips_node = TipsNode([], self.qid_attributes)
        return tips_node

    def test_tree_setup(self):
        # act
        tips_root = setup_tips_root_node(self.raw_test_data, self.qid_attributes)

        # assert
        self.assertEqual(len(tips_root.raw_records), len(self.raw_test_data),
                         "all raw records must be included in most generalized node")

    def test_total_number_of_potential_children(self):
        # act
        tips_root = setup_tips_root_node(self.raw_test_data, self.qid_attributes)
        childcounters: ChildCounters = tips_root.get_child_counters()

        # assert
        count = 0
        for attr_index in childcounters:
            for gen_label in childcounters[attr_index]:
                count += childcounters[attr_index][gen_label]

        # total number of children (for each attribute index) must be equal the number of records
        self.assertEqual(tips_root.number_of_records*len(childcounters), count)

    def test_number_of_records(self):
        # arrange
        tips_root = setup_tips_root_node(self.raw_test_data, self.qid_attributes)

        # act
        nr = tips_root.number_of_records

        # assert
        self.assertEqual(len(self.raw_test_data), nr)

    def test_extract_counter(self):
        # arrange
        tips_root = setup_tips_root_node(self.raw_test_data, self.qid_attributes)

        # act
        counter: TipsNodeCounter = tips_root.extract_counter()

        # assert
        self.assertEqual(counter[0], tips_root.number_of_records)
        self.assertEqual(counter[1], tips_root.get_child_counters())

    def test_set_counters(self):
        # arrange
        tips_node = self.zero_node()

        # act
        tips_node.set_counter_values(self.tips_counters1)

        # assert
        self.assertEqual(tips_node.number_of_records, self.tips_counters1[0])
        self.assertEqual(list(tips_node.get_child_counters()[1].values())[0],
                         list(self.tips_counters1[1][1].values())[0],
                         "counters should have changed, not be zero")

    def test_get_refined_child_nodes(self):
        # arrange
        tips_node = TipsNode(self.raw_test_data, self.qid_attributes)
        attribute_to_refine = 1

        # act
        children: List[TipsNode] = tips_node.get_refined_child_nodes(attribute_to_refine)

        # assert
        self.assertEqual(len(tips_node.qid_attribute_trees[attribute_to_refine].children), len(children))

    def test_extract_counter_information_data(self):
        # arrange
        tips_root = setup_tips_root_node(self.raw_test_data, self.qid_attributes)
        children: List[TipsNode] = tips_root.get_refined_child_nodes(1)

        # act
        counter_information: CounterInformationData = extract_counter_information_data_from_tips_nodes(children)

        # assert
        self.assertEqual(len(counter_information), 2)
        for child in children:
            self.assertEqual(child.extract_counter(), counter_information[child.id])

    def test_perform_refinement(self):
        # arrange
        tips_root = setup_tips_root_node(self.raw_test_data, self.qid_attributes)
        leaf_nodes = setup_tips_leaf_nodes(tips_root)

        attr_index = 1
        best_refinements = {tips_root.id: attr_index}

        # act
        new_leaf_nodes, new_node_list = perform_refinements(leaf_nodes, best_refinements)

        # assert
        self.assertEqual(len(new_leaf_nodes), len(tips_root.qid_attribute_trees[attr_index].children))
        self.assertEqual(len(new_node_list), len(tips_root.qid_attribute_trees[attr_index].children))

    def test_perform_multiple_refinements(self):
        # arrange
        tips_root = setup_tips_root_node(self.raw_test_data, self.qid_attributes)
        leaf_nodes = setup_tips_leaf_nodes(tips_root)
        leaf_nodes_for_test, new_nodes_for_test = perform_refinements(leaf_nodes, {tips_root.id: 2})

        attr_index = 1
        best_refinements = {
            new_nodes_for_test[0].id: attr_index,
            new_nodes_for_test[1].id: attr_index,
        }

        # act
        new_leaf_nodes, new_node_list = perform_refinements(leaf_nodes_for_test, best_refinements)

        # assert
        self.assertEqual(len(new_leaf_nodes), sum(len(node.qid_attribute_trees[attr_index].children) for node in new_nodes_for_test))
        self.assertEqual(len(new_node_list), sum(len(node.qid_attribute_trees[attr_index].children) for node in new_nodes_for_test))

    def test_get_anon_data_result(self):
        # arrange
        tips_root = setup_tips_root_node(self.raw_test_data, self.qid_attributes)
        leaf_nodes = setup_tips_leaf_nodes(tips_root)
        attr_index = 1
        best_refinements = {tips_root.id: attr_index}
        new_leaf_nodes = perform_refinements(leaf_nodes, best_refinements)

        # act
        data: Data = get_anonymous_result_data(new_leaf_nodes)

        # assert
        for row in data:
            found_equal_label = False
            for child in self.qid_attributes[attr_index].children:
                found_equal_label = found_equal_label or row[attr_index] == child.node_label()
            self.assertTrue(found_equal_label, "Label " + row[attr_index] + " is not among qid hierarchy child nodes.")

    def test_tips_node_without_qid_tree_raises_error(self):
        with self.assertRaises(ValueError):
            TipsNode(self.raw_test_data, {})


if __name__ == '__main__':
    unittest.main()
