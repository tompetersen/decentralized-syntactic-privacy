import json
import pickle
import statistics
import time
from typing import List, Optional

from src.box import Box
from src.central import Central
from src.constants import Data, REQUEST_TYPE, RequestType, CENTRAL_PK, INFO, DATA_ROWS, BEST_REFINEMENTS
from src.data_utils import data_fulfills_k_anonymity, compute_equivalence_class_sizes, extract_equivalence_classes
from src.qid_hierarchy_node import QidAttributeTrees, NumericalQidHierarchyNode, CategoricalQidHierarchyNode


class AlgorithmRunner:

    def __init__(self):
        self.k = 0
        self.qid_attribute_trees = None
        self.data_categories = None

        # These values are used as replacement for a real communication channel.
        self.central_pk = None
        self.current_counter_information = None
        self.best_refinements = None
        self.current_counter_information = None
        self.data_rows = None
        self.data_rows = None
        self.current_counter_information = None

        self.number_of_rounds = 0
        self.central: Optional[Central] = None
        self.boxes: Optional[List[Box]] = None

        self.result_data = None

    def run_algorithm(self, qid_attribute_trees: QidAttributeTrees, box_data: List[Data], data_categories, k: int, criteria) -> Data:
        """
        Run the algorithm "in-place" without real communication, but apart from that just like it would happen in the distributed setting.

        :param qid_attribute_trees: the refinement hierarchies
        :param box_data: the data of all boxes, the number of participating boxes is derived from this
        :param data_categories: the data categories
        :param k: the anonymity parameter
        :param criteria: the request criteria
        :return: the anonymized data
        """
        self.k = k
        self.qid_attribute_trees = qid_attribute_trees
        self.data_categories = data_categories

        # initialisation

        self.central_pk = None
        self.current_counter_information = None
        self.best_refinements = None
        self.current_counter_information = None
        self.data_rows = None
        self.data_rows = None
        self.current_counter_information = None

        self.number_of_rounds = 0
        self.number_of_messages = 0
        self.number_of_exchanged_bytes = 0  # estimation without taking encryption into account
        self.start_time = time.perf_counter()

        # initial round

        self.central = Central(k, qid_attribute_trees, criteria, self._central_send_data)
        self.central.start_initial_round()

        self.boxes: List[Box] = []
        for data in box_data:
            box = Box(data_categories, data, criteria, self.central_pk, qid_attribute_trees, self._box_send_data)
            box.perform_initial_round(self.current_counter_information)
            self.boxes.append(box)

        self.central.complete_round(self.current_counter_information)

        # regular rounds

        while self.central.can_perform_round():
            self.number_of_rounds += 1
            self.central.start_round()

            for box in self.boxes:
                box.perform_regular_round(self.best_refinements, self.current_counter_information)

            self.central.complete_round(self.current_counter_information)

        # final step (secure set union)

        self.central.start_secure_data_union()
        for box in self.boxes:
            box.perform_secure_data_union_action(self.data_rows)

        self.result_data = self.central.complete_secure_data_union(self.data_rows)

        # finalisation

        self.end_time = time.perf_counter()

        return self.result_data

    def _update_exchanged_messages(self, data):
        class JSONEncoder(json.JSONEncoder):
            """ Just used as an estimation of exchanged message bytes. """
            def default(self, obj):
                # print("encoding {} of type {}".format(obj, type(obj)))

                if isinstance(obj, bytes):
                    return obj.hex()
                if isinstance(obj, NumericalQidHierarchyNode):
                    obj_dict = dict({
                        'min': obj.min,
                        'max': obj.max,
                        'children': [JSONEncoder.default(self, c) for c in obj.children] if len(obj.children) > 0 else None,
                    })
                    return obj_dict

                if isinstance(obj, CategoricalQidHierarchyNode):
                    obj_dict = {
                        'value': str(obj.value),
                        'children': [JSONEncoder.default(self, c) for c in obj.children] if len(obj.children) > 0 else None,
                    }
                    return obj_dict

                return json.JSONEncoder.default(self, obj)

        self.number_of_messages += 1
        exchanged_str = json.dumps(data, cls=JSONEncoder)
        exchanged_bytes = len(exchanged_str.encode('utf-8'))
        # print("Adding bytes for {} [{}]".format(exchanged_str[:5], exchanged_bytes))
        self.number_of_exchanged_bytes += exchanged_bytes

    def _central_send_data(self, data):
        self._update_exchanged_messages(data)

        if data[REQUEST_TYPE] == RequestType.INFORMATION:
            self.central_pk = pickle.loads(data[CENTRAL_PK])
            self.current_counter_information = data[INFO]
        elif data[REQUEST_TYPE] == RequestType.INSTRUCTION:
            self.best_refinements = data[BEST_REFINEMENTS]
            self.current_counter_information = data[INFO]
        elif data[REQUEST_TYPE] == RequestType.END:
            self.data_rows = data[DATA_ROWS]
        else:
            raise ValueError("unknown RequestType: " + data[REQUEST_TYPE] + ". Adjust integration test.")

    def _box_send_data(self, data):
        self._update_exchanged_messages(data)

        if data[REQUEST_TYPE] == RequestType.END:
            self.data_rows = data[DATA_ROWS]
        else:
            self.current_counter_information = data[INFO]

    def printable_anonymization_run_information(self) -> str:
        """
        Create some information about the algorithm run after finishing.

        :param result_data: the resulting anonymized data
        :param relevant_attributes: the attributes, which have been anonymized
        :param k: the parameter k
        :return: some information about this run in printable format
        """
        if not self.result_data:
            raise Exception("Runner has not run complete algorithm")

        relevant_attributes = list(self.qid_attribute_trees.keys())

        data_is_k_anonymous = data_fulfills_k_anonymity(self.result_data, relevant_attributes, self.k)
        example_anonymous_row = list(zip(self.data_categories, self.result_data[0]))
        eq_class_sizes_counter = compute_equivalence_class_sizes(self.result_data, relevant_attributes)
        eq_class_sizes_counter_sorted = sorted(eq_class_sizes_counter.items(), key=lambda pair: pair[0])
        extracted_eq_classes = extract_equivalence_classes(self.result_data, relevant_attributes)
        eq_class_sizes = sorted([len(eqc) for eqc in extracted_eq_classes.values()])
        eq_class_sizes_mean = statistics.mean(eq_class_sizes)
        eq_class_sizes_median = statistics.median(eq_class_sizes)

        result = ["""FINISHED

Algorithm rounds: {}
Algorithm total time: {:0.2f} s
Messages sent: {}
Estimated total message sizes: {} bytes
Result is k-anonymous: {}

----

Example row of resulting anonymized data:

{}

----

Mean of equivalence class sizes: {}
Median of equivalence class sizes: {}
Distribution of equivalence class sizes: {}

----

Resulting equivalence classes:
    """.format(self.number_of_rounds,
               self.end_time - self.start_time,
               self.number_of_messages,
               self.number_of_exchanged_bytes,
               data_is_k_anonymous,
               example_anonymous_row,
               eq_class_sizes_mean,
               eq_class_sizes_median,
               eq_class_sizes_counter_sorted,
               )]
        for eq, data_rows in extracted_eq_classes.items():
            result.append("\t{}\t\t{}".format(eq, len(data_rows)))

        return "\n".join(result)