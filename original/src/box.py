import pickle
from random import shuffle
from typing import List, Any

from nacl.public import PublicKey

from src import communication
from src.communication import Party
from src.constants import REQUEST_TYPE, RequestType, CRITERIA, INFO, QID_ATTRIBUTE_TREES, CENTRAL_PK, \
    EncryptedData, DATA_ROWS, BEST_REFINEMENTS, BestRefinements, PARTIES, TipsNodeId, AttributeIndex, \
    GeneralizationLabel, BEST_ATTRIBUTE_INDEX, BEST_LABEL
from src.counter_information_data import CounterInformationData, add_counter_information_data
from src.crypto import encrypt_data_rows
from src.qid_hierarchy_node import QidAttributeTrees
from src.tips_nodes import setup_tips_root_node, setup_tips_leaf_nodes, \
    extract_counter_information_data_from_tips_nodes, get_anonymous_result_data, LeafNodes, perform_refinements, \
    LinkHeads, setup_tips_link_heads, perform_refinement, get_anonymous_result_data_from_link_heads


class Box:
    """
    A Box is responsible for performing tasks for exactly ONE request.
    """

    def __init__(self,
                 categories: List[str],
                 data: List[List[Any]],
                 request_criteria: List,
                 central_pk: PublicKey,
                 qid_attribute_trees: QidAttributeTrees,
                 box_id: int,
                 parties: List[Party]):
        """
        Initialize the box component.

        :param categories: categories present in the local data
        :param data: the local data
        :param request_criteria: the criteria for the request
        :param central_pk: the public key of the central component
        :param counter_information: initial count statistics from the previous box/central component in the ring
        :param qid_attribute_trees: the unspecialized qid attribute hierarchies
        :param send_data_callable: a callable to send data to the next box on the ring topology
        """
        self._request_criteria = request_criteria

        for t in qid_attribute_trees.values():
            t.check_consistency()
        self._qid_attribute_trees = qid_attribute_trees

        data_matching_criteria = self._gather_box_data_for_request(request_criteria, categories, data)
        self._tips_root = setup_tips_root_node(data_matching_criteria, qid_attribute_trees)
        self._tips_link_heads: LinkHeads = setup_tips_link_heads(self._tips_root, qid_attribute_trees)

        self._central_pk = central_pk
        self._parties = parties

        self._box_id = box_id
        next_party = list(filter(lambda p: p.id == box_id + 1, parties))
        self._next_party = next_party[0] if next_party else self._parties[0]  # next party by id if present, central otherwise

    def perform_initial_round(self, counter_information: CounterInformationData):
        """
        Perform the initial round:
        Compute local count statistics, add them with received count statistics and forward this data.
        """
        own_counter_information: CounterInformationData = extract_counter_information_data_from_tips_nodes([self._tips_root])
        counter_result = add_counter_information_data(own_counter_information, counter_information)

        send_data = {
            REQUEST_TYPE: RequestType.INFORMATION,
            CRITERIA: self._request_criteria,
            INFO: counter_result,
            QID_ATTRIBUTE_TREES: self._qid_attribute_trees,
            CENTRAL_PK: pickle.dumps(self._central_pk),
            PARTIES: self._parties
        }

        communication.send_data_to_other_party(send_data, self._next_party.host, self._next_party.ring_port)

    @staticmethod
    def _gather_box_data_for_request(criteria: List, data_categories, data):
        # start with full database and filter rows not compliant with criteria
        result = data.copy()
        for criterion in criteria:
            new_result = []

            category = criterion[0]
            operator = criterion[1]
            raw_value = criterion[2]

            if category in data_categories:
                index = data_categories.index(category)
                try:
                    value = int(raw_value)
                except ValueError:
                    try:
                        value = float(raw_value)
                    except ValueError:
                        print("This is not a numerical value: " + raw_value)
                        result = []
                        break

                for row in result:
                    if (
                            (operator == "=" and row[index] == value)
                            or (operator == "<" and row[index] < value)
                            or (operator == ">" and row[index] > value)
                    ):
                        def remove_center_nr(data_row):
                            data_row[0] = "*"

                        remove_center_nr(row)
                        new_result.append(row)
            else:
                print("Criterion '" + category + "' is not present in my database.")
            result = new_result
        return result

    def perform_regular_round(self, best_index: AttributeIndex, best_label: GeneralizationLabel, counter_information: CounterInformationData):
        """
        Performs the actions required for a algorithm round: refine local data based on the given best refinement
        and send the new count statistics to the next box.
        """
        self._tips_link_heads, new_nodes = perform_refinement(self._tips_link_heads, best_index, best_label)

        # extract counter nodes for the new (refined) TIPS nodes
        own_counter_information: CounterInformationData = extract_counter_information_data_from_tips_nodes(new_nodes)
        counter_information_result = add_counter_information_data(counter_information, own_counter_information)

        data = {
            REQUEST_TYPE: RequestType.INSTRUCTION,
            INFO: counter_information_result,
            BEST_ATTRIBUTE_INDEX: best_index,
            BEST_LABEL: best_label
        }

        communication.send_data_to_other_party(data, self._next_party.host, self._next_party.ring_port)

    def perform_secure_data_union_action(self, data_rows: EncryptedData):
        """
        Perform the actions required for the final secure set union algorithm phase:
        encrypt local data, combine encrypted data, shuffle lists, send data to successor.

        :param data_rows: the encrypted result data rows coming from the previous box/central unit
        """
        anonymized_rows = get_anonymous_result_data_from_link_heads(self._tips_link_heads)

        my_encrypted_rows = encrypt_data_rows(anonymized_rows, self._central_pk)
        my_encrypted_rows.extend(data_rows)

        # shuffle to make data origin less obvious
        shuffle(my_encrypted_rows)

        data = {
            REQUEST_TYPE: RequestType.END,
            DATA_ROWS: my_encrypted_rows
        }
        # send this box's result to the next box (or the central unit)
        communication.send_data_to_other_party(data, self._next_party.host, self._next_party.ring_port)
