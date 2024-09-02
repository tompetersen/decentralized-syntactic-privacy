import math
from abc import ABC, abstractmethod
from typing import Any, Dict

from anytree import AnyNode, PreOrderIter

from src.constants import GeneralizationLabel, AttributeIndex


class QidHierarchyNodeException(Exception):
    pass


class AbstractQidHierarchyNode(AnyNode, ABC):

    @abstractmethod
    def covers_value(self, value):
        """
        Returns True, if a value in the QID hierarchy is covered by this node.

        :param value:
        :return:
        """
        pass

    @abstractmethod
    def node_label(self) -> GeneralizationLabel:
        """
        Returns human readable range as a label for an equivalence class defined by node. E.g. an age range 65-70.

        :return: the label
        """
        pass

    @abstractmethod
    def check_consistency(self):
        """
        Raises an exception if the node and his children (and childrens children and ... -> recursive strategy)
        form no consistent tree. The meaning of consistent is node type specific.
        """
        pass


class NumericalQidHierarchyNode(AbstractQidHierarchyNode):
    """
    A node for numerical (integer or floating point) QID hierarchies, like, e.g., age values.
    """

    def __init__(self, min: int, max: int, parent: 'NumericalQidHierarchyNode' = None, **kwargs):
        """
        Create numerical QID hierarchy node.

        :param min: node includes values greater than or equal to this value
        :param max: node includes values less than or equal to this value
        :param parent: the parent node in the hierarchy
        """
        if min > max:
            raise ValueError("Min value {} greater than max value {}".format(min, max))

        self.min = min
        self.max = max
        super().__init__(parent, None, **kwargs)

    def node_label(self) -> GeneralizationLabel:
        if self.min == self.max:
            return str(self.min)
        else:
            return str(self.min) + ":" + str(self.max)

    def covers_value(self, value) -> bool:
        return self.min <= value <= self.max

    def check_consistency(self):
        # leaf nodes are always consistent
        if len(self.children) > 0:
            # check children types
            for c in self.children:
                if type(c) != NumericalQidHierarchyNode:
                    raise QidHierarchyNodeException("Node {}: Child has type {}, NumericalQidHierarchyNode expected.".format(self.node_label(), type(c)))

            # check value coverage
            own_range = list(range(self.min, self.max + 1))

            for c in self.children:
                child_range = list(range(c.min, c.max + 1))

                for val in child_range:
                    try:
                        own_range.remove(val)
                    except ValueError:
                        raise QidHierarchyNodeException("Node {}: value {} in child {} is already covered by a sibling or is not in parent range [{} - {}] at all.".format(self.node_label(), c.node_label(), val, self.min, self.max))

            if len(own_range) > 0:
                raise QidHierarchyNodeException("Node {}: Children do not cover the values {}".format(self.node_label(), own_range))

            # check children consistencies
            for c in self.children:
                c.check_consistency()

    @staticmethod
    def create_balanced_numerical_hierarchy(minv: int, maxv: int, parent=None) -> 'NumericalQidHierarchyNode':
        """ Create a balanced QID hierarch tree by splitting the domain in two parts as long as possible. """
        node = NumericalQidHierarchyNode(minv, maxv, parent=parent)
        diff = maxv - minv
        if diff > 0:
            diff_half = math.floor(diff / 2)
            NumericalQidHierarchyNode.create_balanced_numerical_hierarchy(minv, minv + diff_half, node)
            NumericalQidHierarchyNode.create_balanced_numerical_hierarchy(minv + diff_half + 1, maxv, node)
        return node


class CategoricalQidHierarchyNode(AbstractQidHierarchyNode):
    """
    A node for categorical QID hierarchies, like, e.g., the gender or profession.
    """

    def __init__(self, value: Any, parent: 'CategoricalQidHierarchyNode' = None, **kwargs):
        """
        Create categorical QID hierarchy node.

        :param value: the value of this node. Must be the exact value for "leaf" nodes
        :param parent: the parent node in the hierarchy
        """
        self.value = value

        super().__init__(parent, None, **kwargs)

    def node_label(self) -> GeneralizationLabel:
        return self.value

    def covers_value(self, value) -> bool:
        # covers value, if the value is its own value or a value of a child
        return self.value == value or any(c.covers_value(value) for c in self.children)

    def check_consistency(self):
        # leaf nodes are always consistent
        if len(self.children) > 0:
            # check children types
            for c in self.children:
                if type(c) != CategoricalQidHierarchyNode:
                    raise QidHierarchyNodeException("Node {}: Child has type {}, CategoricalQidHierarchyNode expected.".format(self.node_label(), type(c)))

            # check for duplicated values in subtree
            children_with_same_value = [c for c in PreOrderIter(self, filter_=lambda n: n != self) if c.value == self.value]
            if len(children_with_same_value) > 0:
                def child_path(child):
                    current = child
                    p = []
                    while current != self:
                        p.append(current.node_label())
                        current = current.parent
                    p.reverse()
                    return " -> ".join(p)

                paths = " | ".join([child_path(child) for child in children_with_same_value])
                raise QidHierarchyNodeException("Node {}: Nodes in the subtree contain own node value: {}".format(self.node_label(), paths))

            # check children consistencies
            for c in self.children:
                c.check_consistency()


QidAttributeTrees = Dict[AttributeIndex, AbstractQidHierarchyNode]