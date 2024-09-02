import pickle
import time
from operator import itemgetter
from random import randint
from typing import List, Callable, Dict, Any, Optional, Tuple

from src import motion, communication, counter_information_data
from src.constants import REQUEST_TYPE, RequestType, CRITERIA, INFO, QID_ATTRIBUTE_TREES, CENTRAL_PK, \
    BEST_REFINEMENTS, DATA_ROWS, NR_DUMMIES_MIN, NR_DUMMIES_MAX, DUMMY_ROW, DUMMY, EncryptedData, Data, \
    BestRefinements, PARTIES, BEST_ATTRIBUTE_INDEX, BEST_LABEL
from src.counter_information_data import CounterInformationData, counter_information_data_with_random_numbers, \
    substract_counter_information_data, counter_groups_from_counter_information_data, NodeCounterType, \
    CounterGroup, node_ids_from_counter_groups
from src.crypto import generate_keys, encrypt_data_rows, decrypt_result
from src.qid_hierarchy_node import QidAttributeTrees
from src.tips_nodes import setup_tips_root_node, setup_tips_leaf_nodes, TipsNode, perform_refinements, \
    extract_counter_information_data_from_tips_nodes, LeafNodes, find_best_refinements, setup_tips_link_heads, \
    LinkHeads, perform_refinement, find_best_tips_link_head


class Central:
    """ A Central is responsible for performing tasks for exactly ONE request. """

    CENTRAL_ID = 0

    def __init__(self, k: int, qid_attribute_trees: QidAttributeTrees, criteria_list: List, parties: [motion.Party], central_host, central_ring_port, central_motion_port):
        """
        Initialize central component.

        :param k: the anonymity parameter for k-anonymity
        :param criteria_list: the requested criteria
        :param send_data: a callable to send data to the next box in the ring topology
        """
        self.k = k
        self.criteria_list = criteria_list

        for t in qid_attribute_trees.values():
            t.check_consistency()
        self.qid_attribute_trees = qid_attribute_trees

        self._private_key, self._public_key = generate_keys()

        tips_root = setup_tips_root_node(raw_data_rows=None, qid_attributes=self.qid_attribute_trees)
        self._tips_link_heads: LinkHeads = setup_tips_link_heads(tips_root, self.qid_attribute_trees)
        self._newest_tips_nodes: List[TipsNode] = [tips_root]
        # TODO LH which of these variables are still necessary for easy motion usage?
        # self._leaf_nodes: LeafNodes = setup_tips_leaf_nodes(tips_root)
        self._newest_counter_inf_data: Optional[CounterInformationData] = None
        self._relevant_counter_groups: Optional[List[CounterGroup]] = None

        self._best_refinement: Optional[Tuple[int, str]] = None

        if len(parties) <= 1:
            raise Exception("we require more than 1 party")
        for idx, p in enumerate(parties):
            if idx + 1 != p.id:
                raise Exception("we expect ascending ids starting with 1, given: {}".format(parties))
        self._parties = parties
        self._first_party = parties[0]  # used for ring topology
        central_party = motion.Party(self.CENTRAL_ID, central_host, central_ring_port, central_motion_port)
        self._parties.insert(0, central_party)  # add central as party for other boxes

    def start_initial_round(self):
        """
        Start the initial round of the algorithm to collect initial count statistics (via secure sum protocol).
        """
        self._newest_counter_inf_data = extract_counter_information_data_from_tips_nodes(self._newest_tips_nodes)
        self._relevant_counter_groups = counter_groups_from_counter_information_data(self._newest_counter_inf_data, only_undefined=True)
        relevant_tips_node_ids = node_ids_from_counter_groups(self._relevant_counter_groups)

        print(f"Central initial round: {relevant_tips_node_ids}", flush=True)

        data = {
            REQUEST_TYPE: RequestType.INFORMATION,
            CRITERIA: self.criteria_list,
            INFO: relevant_tips_node_ids,
            QID_ATTRIBUTE_TREES: self.qid_attribute_trees,
            CENTRAL_PK: pickle.dumps(self._public_key),
            PARTIES: self._parties
        }

        # query leading box
        communication.send_data_to_other_party(data, self._first_party.host, self._first_party.ring_port)

    def can_perform_round(self) -> bool:
        """
        Returns, whether another round can be performed, meaning if the data can be further specialized.

        :return: True, if the data can be further specialized
        """
        return self._best_refinement is not None

    def start_round(self):
        """
        Start a regular round of the algorithm:
        Refine the best suited attribute generalization and collect new count statistics (via secure sum protocol).
        """
        best_attr_index, best_label = self._best_refinement
        self._tips_link_heads, self._newest_tips_nodes = perform_refinement(self._tips_link_heads, best_attr_index,
                                                                            best_label)

        self._newest_counter_inf_data = extract_counter_information_data_from_tips_nodes(self._newest_tips_nodes)
        self._relevant_counter_groups = counter_groups_from_counter_information_data(self._newest_counter_inf_data, only_undefined=True)
        relevant_tips_node_ids = node_ids_from_counter_groups(self._relevant_counter_groups)

        print(f"Central regular round: {relevant_tips_node_ids}", flush=True)

        data = {
            REQUEST_TYPE: RequestType.INSTRUCTION,
            INFO: relevant_tips_node_ids,
            BEST_ATTRIBUTE_INDEX: best_attr_index,
            BEST_LABEL: best_label
        }

        communication.send_data_to_other_party(data, self._first_party.host, self._first_party.ring_port)

    def complete_round(self, blinded_counter_information: CounterInformationData):
        """
        Completes a round by integrating received count statistics (via secure sum protocol).

        :param blinded_counter_information: the (blinded) count statistics
        """
        # run motion
        motion_result_counters = motion.perform_protocol_secure_sums_gt_k(self._parties,
                                                                          self.CENTRAL_ID,
                                                                          self._relevant_counter_groups,
                                                                          self.k
                                                                          )

        # incorporate motion results in counter_inf_data/leaf_nodes
        self._newest_counter_inf_data = counter_information_data.incorporate_counter_groups(self._newest_counter_inf_data,
                                                                                            motion_result_counters)
        for node in self._newest_tips_nodes:
            node.set_counter_values(self._newest_counter_inf_data[node.id])

        self._best_refinement = find_best_tips_link_head(self._tips_link_heads, self.k)
        print(f"Next best refinement: {self._best_refinement}", flush=True)

    def start_secure_data_union(self):
        """
        Start the final algorithm phase: Collecting the data via secure set union protocol.
        """
        dummies = self._generate_dummies()
        encrypted_rows = encrypt_data_rows(dummies, self._public_key)

        data = {
            REQUEST_TYPE: RequestType.END,
            DATA_ROWS: encrypted_rows
        }

        communication.send_data_to_other_party(data, self._first_party.host, self._first_party.ring_port)

    @staticmethod
    def _generate_dummies(number_of_dummies: int = randint(NR_DUMMIES_MIN, NR_DUMMIES_MAX)) -> Data:
        def generate_dummy_row():
            row = DUMMY_ROW.copy()
            row[0] = DUMMY
            row[1] = randint(0, 100)
            return row

        return [generate_dummy_row() for _ in range(number_of_dummies)]

    def complete_secure_data_union(self, encrypted_result: EncryptedData) -> Data:
        """
        Complete the final algorithm phase.

        :param encrypted_result: the encrypted received secure set union protocol result data
        :return: the anonymized result data
        """
        anonymized_result = decrypt_result(encrypted_result, self._private_key)
        anonymized_result_without_dummies = [item for item in anonymized_result if item[0] != DUMMY]
        sorted_anon_result = sorted(anonymized_result_without_dummies, key=itemgetter(1))

        return sorted_anon_result
