"""
Run a box via terminal.
Currently this uses simple communication via sockets and data pickling and a fixed data set.
"""
import argparse
import pickle

import adult_data
import medical_data
from src.box import Box
from src.communication import receive_data
from src.constants import DATA_ROWS, REQUEST_TYPE, QID_ATTRIBUTE_TREES, \
    CRITERIA, CENTRAL_PK, INFO, RequestType, PARTIES, BEST_ATTRIBUTE_INDEX, BEST_LABEL
from src.data_utils import read_csv_data


def answer_request(box_data, box_data_categories, box_id: int, box_host: str, box_ring_port: int):
    """
    Perform the required steps in the distributed algorithm to compute a request result.

    :param box_data: the local data
    :param box_data_categories: categories in the local data
    :param box_id: the box id
    :param box_ring_port: the box port for ring communication
    :param box_host: the box host
    :return:
    """

    # wait for connections
    request_from_predecessor = receive_data(box_host, box_ring_port)

    # data = {REQUEST_TYPE: RequestType.INFORMATION,
    #         CRITERIA: criteria_list,
    #         INFO: counter_link_heads_init,
    #         QID_ATTRIBUTE_TREES: qid_attribute_trees,
    #         CENTRAL_PK: pickle.dumps(public_key)}

    central_pk = pickle.loads(request_from_predecessor[CENTRAL_PK])
    criteria = request_from_predecessor[CRITERIA]
    qid_trees = request_from_predecessor[QID_ATTRIBUTE_TREES]
    counter_information_data = request_from_predecessor[INFO]
    parties = request_from_predecessor[PARTIES]

    b = Box(box_data_categories, box_data, criteria, central_pk, qid_trees, box_id, parties)
    b.perform_initial_round(counter_information_data)

    while True:
        request_from_predecessor = receive_data(box_host, box_ring_port)

        # data = {REQUEST_TYPE: RequestType.INSTRUCTION,
        #         INFO: extracted_counter_nodes,
        #         BEST_REFINEMENTS: best_refinements}

        # data = {REQUEST_TYPE: RequestType.END,
        #         DATA_ROWS: encrypted_rows}

        if request_from_predecessor[REQUEST_TYPE] == RequestType.INSTRUCTION:
            best_attr_index = request_from_predecessor[BEST_ATTRIBUTE_INDEX]
            best_gen_label = request_from_predecessor[BEST_LABEL]
            counter_information_data = request_from_predecessor[INFO]

            b.perform_regular_round(best_attr_index, best_gen_label, counter_information_data)
        elif request_from_predecessor[REQUEST_TYPE] == RequestType.END:
            data_rows = request_from_predecessor[DATA_ROWS]

            b.perform_secure_data_union_action(data_rows)
            break
        else:
            raise Exception("Unexpected request type: {}".format(request_from_predecessor[REQUEST_TYPE]))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('boxid', type=int, help='The id for the box. If no more arguments are given, it is used to set the box ports.')
    parser.add_argument('number_of_boxes', type=int, help='Number of participating boxes used for data splitting')
    parser.add_argument('--address', help='The box ip address.', default="127.0.0.1")
    parser.add_argument('--ringport', type=int, help='The box port for ring communication.')
    parser.add_argument('--motionport', type=int, help='The box port for MOTION communication.')
    parser.add_argument('--dataset', help='The data set to be used ([medical]/adult).', choices=["adult", "medical"], default="medical")

    args = parser.parse_args()

    box_id = args.boxid
    box_host = args.address
    box_ring_port = args.ringport if args.ringport else 4442 + box_id
    box_motion_port = args.motionport if args.motionport else 5442 + box_id

    print("starting box ({}, {}, {}, {})".format(box_id, box_host, box_ring_port, box_motion_port))
    print("reading data...")

    datapath = medical_data.DATA_PATH if args.dataset == "medical" else adult_data.DATA_PATH
    data_categories, all_data = read_csv_data(datapath)
    box_data_range = len(all_data) // args.number_of_boxes
    box_data = all_data[(box_id - 1) * box_data_range:box_id * box_data_range]

    print("finished reading data.")
    print("\nWaiting for requests on port " + str(box_ring_port) + "\n")

    answer_request(box_data, data_categories, box_id, box_host, box_ring_port)


if __name__ == "__main__":
    main()
