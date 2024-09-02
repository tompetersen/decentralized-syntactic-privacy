from collections import defaultdict
from copy import deepcopy
from typing import List, Dict, Tuple, Optional

import src.counter_information_data
from src.constants import AttributeIndex, GeneralizationLabel, TipsNodeId, Data, BestRefinements
from src.counter_information_data import TipsNodeCounter, ChildCounters, CounterInformationData
from src.qid_hierarchy_node import QidAttributeTrees


class TipsNode:
    def __init__(self, raw_records: Optional[Data], qid_attr_trees: QidAttributeTrees):
        if len(qid_attr_trees) < 1:
            raise ValueError("Cannot instantiate TIPS node without QID-attributes.")

        self.raw_records: Data = raw_records
        self.node_counter_info = self._get_node_counter_info(raw_records)
        self.qid_attribute_trees = qid_attr_trees
        self._potential_child_counters: ChildCounters = self._init_potential_child_counters()
        self.id: TipsNodeId = self._generate_id()

    def number_of_records(self):
        return self.node_counter_info[1]

    def _get_node_counter_info(self, raw_records) -> src.counter_information_data.NodeCounterInfo:
        if raw_records is None:
            return src.counter_information_data.NodeCounterType.Undefined, 0
        else:
            return src.counter_information_data.NodeCounterType.DataContent, len(raw_records)

    def _generate_id(self, specialize_attr_index=None, specialize_node_label=None) -> TipsNodeId:
        """
        Generate an id for this node.

        Include specialize_attr_index if you want to generate a fully qualified id for a potential child given by the
        specialize_node_label.
        """
        result = ""

        for attr_index in self.qid_attribute_trees:
            if attr_index == specialize_attr_index:
                result += str(attr_index) + "." + specialize_node_label + "|"
            else:
                result += str(attr_index) + "." + self.qid_attribute_trees[attr_index].node_label() + "|"

        return result

    def _init_potential_child_counters(self) -> ChildCounters:
        """
        Determines whether the records of this node may be refined for the given attribute (index).
        Should only be called once during initialization as this is an expensive operation.
        """
        # TODO JS, TP: Cache data rows associated with each child and re-use in get_refined_child_nodes()
        # goal: No need to iterate over data AGAIN when get_refined_child_nodes is executed
        result = {}

        for qid_index in self.qid_attribute_trees:
            qid_node_children = self.qid_attribute_trees[qid_index].children
            child_counters = {}
            for child in qid_node_children:
                child_id = self._generate_id(qid_index, child.node_label())  # use fully qualified labels for children here
                if self.raw_records is not None:
                    counter = 0
                    for row in self.raw_records:
                        value_to_check = row[qid_index]
                        if child.covers_value(value_to_check):
                            counter += 1
                    child_counters[child_id] = (src.counter_information_data.NodeCounterType.DataContent, counter)
                else:
                    child_counters[child_id] = (src.counter_information_data.NodeCounterType.Undefined, 0)
            result[qid_index] = child_counters

        return result

    def extract_counter(self) -> TipsNodeCounter:
        """
        Get the counter information (number of records, number of potential children) for this TIPS node.

        :return: the counter information
        """
        return self.node_counter_info, self.get_child_counters()

    def set_counter_values(self, counter: TipsNodeCounter):
        """
        Set the counter values for this TIPS node. This must only be called for nodes without data (= new nodes in the central unit).

        :param counter: the new counter values
        """
        if self.raw_records is not None:
            raise RuntimeError("set_counter_values called for TIPS node containing data")

        # TODO MOT This breaks since we already set the counter during specialization
        # if self.node_counter_info[0] != src.counter_information_data.NodeCounterType.Undefined:
        #     if self.extract_counter() != counter:
        #         print("NODE INFO ALREADY SET")
        #         print("node_id", self.id)
        #         print("node counters: ", self.extract_counter())
        #         print("counters to be set: ", counter)
        #
        #         raise RuntimeError("Trying to set differing counters for node with existing counters")

        self.node_counter_info = counter[0]
        self._potential_child_counters = counter[1]

    def get_child_counters(self) -> ChildCounters:
        """
        Returns the (potential) child counters for this TIPS node.

        :return: the child counters
        """
        return deepcopy(self._potential_child_counters)

    def generalization_label_for_attribute(self, attr_index: AttributeIndex) -> GeneralizationLabel:
        """
        Returns the TIPS nodes generalization class (given by label) for an attribute.

        :param attr_index: the attribute index
        :return: the generalization label
        """
        return self.qid_attribute_trees[attr_index].node_label()

    def get_refined_child_nodes(self, qid_index: AttributeIndex) -> List['TipsNode']:
        """
        Returns the resulting TIPS nodes for a refinement of this node w.r.t one attribute.

        :param qid_index: the attribute to be refined
        :return: the refined TIPS nodes
        """
        try:
            current_qid_attr_tree = self.qid_attribute_trees[qid_index]
        except KeyError:
            raise ValueError("Cannot refine QID index {} because corresponding QID node is not contained in this TIPS-node.".format(qid_index))

        result = []
        for child in current_qid_attr_tree.children:
            child_raw_records = None
            if self.raw_records is not None:
                # set covered data records in children, if data is present
                child_raw_records = []
                for row in self.raw_records:
                    value_to_check = row[qid_index]
                    if child.covers_value(value_to_check):
                        child_raw_records.append(row)

            child_attr_qid_nodes = self.qid_attribute_trees.copy()
            child_attr_qid_nodes[qid_index] = child
            child_node = TipsNode(child_raw_records, child_attr_qid_nodes)

            if self.raw_records is None:
                # set already computed child counters, if data is not present
                new_child_counter = self._potential_child_counters[qid_index][child_node.id]
                child_node.node_counter_info = new_child_counter

            result.append(child_node)

        return result

    def find_best_refinement(self, k: int) -> Optional[AttributeIndex]:
        best_refinement = None
        max_score = 0

        for qid_index, current_hierarchy_node in self.qid_attribute_trees.items():
            if len(current_hierarchy_node.children) > 0:
                c_counters: List[src.counter_information_data.NodeCounterInfo] = list(self._potential_child_counters[qid_index].values())
                if all((c[0] == src.counter_information_data.NodeCounterType.Valid) or (c[0] == src.counter_information_data.NodeCounterType.Empty) for c in c_counters):  # check that refinement does not violate k-anonymity
                    # Note: c==Empty is needed here. Example: 10 records, all with Sex=1. Without allowing c==0, the records
                    # could not be specialized from Sex=ANY and would remain this way (because c==0 for the child Sex=2)
                    # Also note that if c==Empty for all children, the score remains 0.
                    #   But such a node (with no children) would not make sense any way. (JS, Nov2020)

                    # TODO have a look at score function
                    # TODO for now, we take the sum of squared child counters to prioritize larger subsets
                    score = sum(c[1] ** 2 for c in c_counters if c[0] == src.counter_information_data.NodeCounterType.Valid)

                    if score > max_score:
                        best_refinement = qid_index
                        max_score = score

        return best_refinement

    def anonymized_data(self) -> Data:
        """
        TODO
        :return:
        """
        result = []

        for row in self.raw_records:
            new_row = deepcopy(row)
            for qid_index, qid_node in self.qid_attribute_trees.items():
                new_row[qid_index] = qid_node.node_label()
            result.append(new_row)

        return result


# A dictionary containing all TIPS nodes for all generalisations w.r.t. one attribute
LinkHeadsForAttribute = Dict[GeneralizationLabel, List[TipsNode]]

# A dictionary containing all link heads for all attributes
LinkHeads = Dict[AttributeIndex, LinkHeadsForAttribute]

# A dictionary containing the TIPS nodes to be replaced after refinement and the respective new nodes.
# structure { old_tips_node_to_replace : [ new_tips_node_1, new_tips_node_2, ...] }
ReplacementDictionary = Dict[TipsNode, List[TipsNode]]

# A dict containing all leaf nodes of a TIPS tree for faster access.
LeafNodes = Dict[TipsNodeId, TipsNode]


# setup methods

def setup_tips_root_node(raw_data_rows: Optional[Data], qid_attributes: QidAttributeTrees) -> TipsNode:
    """
    Builds single TIPS node as initial tree, including all raw data rows and most generalized qid_nodes.

    :param raw_data_rows: all raw data records
    :param qid_attributes: dictionary of following form { qid_attribute_index: most_generalized_qid_hierarchy_node }
    :return: single TIPS node as initial TIPS tree
    """
    return TipsNode(raw_records=raw_data_rows, qid_attr_trees=qid_attributes)


def setup_tips_leaf_nodes(tips_root: TipsNode) -> LeafNodes:
    """
    TODO
    """
    return {tips_root.id: tips_root}


# refinement methods


def find_best_refinements(leaf_nodes: LeafNodes, k: int) -> BestRefinements:
    """
    TODO
    """
    result = {}

    for node_id, node in leaf_nodes.items():
        best = node.find_best_refinement(k)
        if best is not None:
            result[node_id] = best

    return result


def perform_refinements(leaf_nodes: LeafNodes, best_refinements: BestRefinements) -> LeafNodes:
    """
    TODO
    :param leaf_nodes:
    :param best_refinements:
    :return:
    """
    new_leaf_nodes = leaf_nodes.copy()

    for node_id, best_refinement in best_refinements.items():
        try:
            node = leaf_nodes[node_id]
        except KeyError:
            raise Exception("Node id {} to be refined not present in leaf_nodes".format(node_id))

        child_nodes = node.get_refined_child_nodes(best_refinement)
        new_leaf_nodes.pop(node_id)
        for c in child_nodes:
            new_leaf_nodes[c.id] = c

    return new_leaf_nodes

# END LEAF NODE METHODS

# LINK HEADS METHODS

# setup


def setup_tips_link_heads(tips_root: TipsNode, qid_attributes: QidAttributeTrees) -> LinkHeads:
    """
    TODO
    """
    link_heads = {}

    for qid_index in qid_attributes:
        qid_root_node = qid_attributes[qid_index]
        link_heads[qid_index] = {qid_root_node.node_label(): [tips_root]}

    return link_heads


# find best refinement methods


def find_best_tips_link_head(link_heads: LinkHeads, k: int) -> Optional[Tuple[AttributeIndex, GeneralizationLabel]]:
    """
    Find the best next refinement step for a TIPS tree (given by its link heads) w.r.t. k.

    :param link_heads: the TIPS tree link heads
    :param k: the anonymization parameter k
    :return: the best attribute and generalization equivalence class, or None,  if there is no further specialization possible
    """
    highest_score = 0
    best_attr_index, best_label = None, None

    for attribute_index, link_head in link_heads.items():
        for generalization_label, nodes in link_head.items():
            if _can_be_specialized(attribute_index, generalization_label, link_head):
                score = _calculate_score_for_label(nodes, attribute_index, k)

                if score > highest_score:
                    # found better score, update:
                    highest_score = score
                    best_attr_index, best_label = attribute_index, generalization_label

    if best_attr_index is None and best_label is None:
        return None
    else:
        return best_attr_index, best_label


def _can_be_specialized(attribute_index: AttributeIndex, generalization_label: GeneralizationLabel, link_head: LinkHeadsForAttribute) -> bool:
    """ Return true, if generalization for attribute has child specializations. """
    first_counter_node = next(iter(link_head[generalization_label]))
    potential_qid_children = first_counter_node.qid_attribute_trees[attribute_index].children
    return len(potential_qid_children) > 0


def _calculate_score_for_label(tips_nodes: List[TipsNode], attribute_index: AttributeIndex, k: int) -> int:
    score = 0
    for node in tips_nodes:
        child_counters = node.get_child_counters()[attribute_index].values()  # [(NodeCounterType, int)]
        for child_counter_type, child_count in child_counters:
            if child_counter_type == src.counter_information_data.NodeCounterType.SmallerThanK:
                # cannot be refined, since this would violate k-anonymity.
                # However, 0 children are allowed (but will yield score 0 if all children lists are empty)
                return 0

        score += node.number_of_records() ** 2
    return score


# perform refinement methods


def perform_refinement(tips_link_heads: LinkHeads, best_attr_index: AttributeIndex, best_label: GeneralizationLabel) -> Tuple[LinkHeads, List[TipsNode]]:
    """
    Based on a given TIPS tree (represented by link heads) perform the refinement given by attribute index and generalization label.

    :param tips_link_heads: the TIPS tree link heads
    :param best_attr_index: the attribute to be refined
    :param best_label: the generalization class to be refined
    :return: a tuple consisting of the resulting TIPS tree (represented by link heads) and the new TIPS nodes (already contained in the tree)
    """
    # choose nodes to be refined from best refinement
    tips_nodes_to_refine: List[TipsNode] = tips_link_heads[best_attr_index].pop(best_label)

    # gather child nodes and required replacements for refinement
    new_label_tips_node_dict, replacement_dictionary = _gather_child_nodes_for_refinement(tips_nodes_to_refine, best_attr_index)

    # add new label with tips nodes
    tips_link_heads[best_attr_index].update(new_label_tips_node_dict)

    new_tips_link_heads = _update_link_heads(tips_link_heads, replacement_dictionary)

    # flatten list
    new_node_list = [item for sublist in replacement_dictionary.values() for item in sublist]

    return new_tips_link_heads, new_node_list


def _gather_child_nodes_for_refinement(tips_nodes_to_refine: List[TipsNode], best_attr_index: AttributeIndex) -> Tuple[LinkHeadsForAttribute, ReplacementDictionary]:
    new_label_tips_node_dict = defaultdict(list)
    replacement_dictionary = {}

    for tips_node in tips_nodes_to_refine:
        child_nodes = tips_node.get_refined_child_nodes(best_attr_index)
        replacement_dictionary[tips_node] = child_nodes
        for child_node in child_nodes:
            label = child_node.generalization_label_for_attribute(best_attr_index)
            new_label_tips_node_dict[label].append(child_node)

    return new_label_tips_node_dict, replacement_dictionary


def _update_link_heads(tips_link_heads: LinkHeads, replacement_dictionary: ReplacementDictionary) -> LinkHeads:
    new_tips_link_heads = _customcopy(tips_link_heads)

    for attr_index in tips_link_heads:
        for generalization_label in tips_link_heads[attr_index]:
            tips_node_list = tips_link_heads[attr_index][generalization_label]
            for tips_node in tips_node_list:
                if tips_node in replacement_dictionary:
                    new_tips_link_heads[attr_index][generalization_label].remove(tips_node)
                    new_tips_link_heads[attr_index][generalization_label].extend(replacement_dictionary[tips_node])

    return new_tips_link_heads


def _customcopy(tips_link_heads: LinkHeads) -> LinkHeads:
    link_heads_copy: LinkHeads = {}

    for attr_index in tips_link_heads:
        link_heads_copy[attr_index] = {}
        for generalization_label in tips_link_heads[attr_index]:
            link_heads_copy[attr_index][generalization_label] = []
            tips_node_list: List[TipsNode] = tips_link_heads[attr_index][generalization_label]
            link_heads_copy[attr_index][generalization_label].extend(tips_node_list)

    return link_heads_copy


# END LINK HEADS METHODS


# counter information data methods


def extract_counter_information_data_from_tips_nodes(new_nodes: List[TipsNode]) -> CounterInformationData:
    """
    Extract counter information for a list of TIPS nodes.
    This is used for collecting required counter information for new TIPS nodes during a protocol round,
    which are passed to the next box/the central unit.

    :param new_nodes: the new TIPS nodes
    :return: the respective counter information
    """
    result: CounterInformationData = {}

    for tips_node in new_nodes:
        node_counter = tips_node.extract_counter()
        result[tips_node.id] = node_counter

    return result


# anonymized result methods


def get_anonymous_result_data(leaf_nodes: LeafNodes) -> Data:
    """
    Based on given TIPS tree leaf nodes extract the resulting (anonymized) data set.

    :param leaf_nodes: the TIPS tree leaf nodes
    :return: the anonymized data set
    """
    result = []

    for node in leaf_nodes.values():
        result.extend(node.anonymized_data())

    return result


def get_anonymous_result_data_from_link_heads(tips_link_heads: LinkHeads) -> Data:
    """
    Based on a given TIPS tree (represented by link heads) extract the resulting (anonymized) data set.
    """
    result = []

    # each attribute has links to the whole dataset, just take the first
    some_attribute_index = next(iter(tips_link_heads))
    for generalization_name in tips_link_heads[some_attribute_index]:
        tips_nodes = tips_link_heads[some_attribute_index][generalization_name]
        for tips_node in tips_nodes:
            result.extend(tips_node.anonymized_data())

    return result

