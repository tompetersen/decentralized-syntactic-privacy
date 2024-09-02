import unittest

from src.qid_hierarchy_node import NumericalQidHierarchyNode, CategoricalQidHierarchyNode, QidHierarchyNodeException
from test.testdata import get_test_data


class NumericalQidHierarchyNodeTest(unittest.TestCase):

    def setUp(self) -> None:
        self.raw_test_data = get_test_data()

    def test_node_label_range(self):
        # arrange
        node = NumericalQidHierarchyNode(1, 2)

        # act
        name = node.node_label()

        # assert
        self.assertEqual("1:2", name)

    def test_node_label_single(self):
        # arrange
        node = NumericalQidHierarchyNode(1, 1)

        # act
        name = node.node_label()

        # assert
        self.assertEqual("1", name)

    def test_covers_value(self):
        # arrange
        node = NumericalQidHierarchyNode(0, 3)

        # act
        does_cover_value1 = node.covers_value(1)
        does_cover_value2 = node.covers_value(2)
        does_not_cover_value1 = node.covers_value(5)
        does_not_cover_value2 = node.covers_value(-1)

        # assert
        self.assertTrue(does_cover_value1)
        self.assertTrue(does_cover_value2)
        self.assertFalse(does_not_cover_value1)
        self.assertFalse(does_not_cover_value2)

    def test_incorrect_value_ranges_raise_error(self):
        self.assertRaises(ValueError, NumericalQidHierarchyNode, 3, 2)

    def test_valid_tree_consistency(self):
        root_node = NumericalQidHierarchyNode(0, 9)
        c1 = NumericalQidHierarchyNode(0, 5, root_node)
        c = NumericalQidHierarchyNode(0, 2, c1)
        c = NumericalQidHierarchyNode(3, 5, c1)
        c2 = NumericalQidHierarchyNode(6, 9, root_node)

        root_node.check_consistency()

    def test_tree_consistency_invalid_type(self):
        root_node = NumericalQidHierarchyNode(0, 9)
        c = CategoricalQidHierarchyNode("test", root_node)

        with self.assertRaises(QidHierarchyNodeException):
            root_node.check_consistency()

    def test_full_child_coverage(self):
        root_node = NumericalQidHierarchyNode(0, 9)
        c = NumericalQidHierarchyNode(0, 5, root_node)

        with self.assertRaises(QidHierarchyNodeException):
            root_node.check_consistency()

    def test_child_value_outside_parent_range(self):
        root_node = NumericalQidHierarchyNode(0, 9)
        c = NumericalQidHierarchyNode(0, 10, root_node)

        with self.assertRaises(QidHierarchyNodeException):
            root_node.check_consistency()

    def test_overlapping_children(self):
        root_node = NumericalQidHierarchyNode(0, 9)
        c = NumericalQidHierarchyNode(0, 5, root_node)
        c = NumericalQidHierarchyNode(5, 9, root_node)

        with self.assertRaises(QidHierarchyNodeException):
            root_node.check_consistency()


class OtherQidHierarchyNodeTest(unittest.TestCase):

    def setUp(self) -> None:
        self.hierarchy_root = CategoricalQidHierarchyNode("ANY")
        self.child_l = CategoricalQidHierarchyNode("left", self.hierarchy_root)
        self.child_r = CategoricalQidHierarchyNode("right", self.hierarchy_root)
        self.child_l_l = CategoricalQidHierarchyNode("left-left", self.child_l)
        self.child_l_r = CategoricalQidHierarchyNode("left-right", self.child_l)

    def test_node_label(self):
        self.assertEqual(self.hierarchy_root.node_label(), "ANY")

    def test_root_covers_all_values(self):
        self.assertTrue(self.hierarchy_root.covers_value("left"))
        self.assertTrue(self.hierarchy_root.covers_value("right"))
        self.assertTrue(self.hierarchy_root.covers_value("left-left"))
        self.assertTrue(self.hierarchy_root.covers_value("left-right"))

    def test_parent_covers_child(self):
        self.assertTrue(self.child_l.covers_value("left-left"))

    def test_child_does_not_cover_parent(self):
        self.assertFalse(self.child_l_l.covers_value("ANY"))
        self.assertFalse(self.child_l_l.covers_value("left"))

    def test_valid_tree_consistency(self):
        root = CategoricalQidHierarchyNode("ANY")
        c1 = CategoricalQidHierarchyNode("sub1", root)
        c = CategoricalQidHierarchyNode("sub2", root)
        c = CategoricalQidHierarchyNode("sub3", c1)
        c = CategoricalQidHierarchyNode("sub4", c1)

    def test_duplicated_value_in_child(self):
        root = CategoricalQidHierarchyNode("ANY")
        c1 = CategoricalQidHierarchyNode("sub1", root)
        c = CategoricalQidHierarchyNode("ANY", root)

        with self.assertRaises(QidHierarchyNodeException):
            root.check_consistency()

    def test_duplicated_value_in_grand_child(self):
        root = CategoricalQidHierarchyNode("ANY")
        c1 = CategoricalQidHierarchyNode("sub1", root)
        c2 = CategoricalQidHierarchyNode("sub2", root)
        c = CategoricalQidHierarchyNode("ANY", c1)
        c = CategoricalQidHierarchyNode("sub4", c1)
        c = CategoricalQidHierarchyNode("ANY", c2)
        c = CategoricalQidHierarchyNode("sub5", c2)

        with self.assertRaises(QidHierarchyNodeException):
            root.check_consistency()


if __name__ == '__main__':
    unittest.main()
