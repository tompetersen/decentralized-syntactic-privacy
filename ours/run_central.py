"""
Run the central unit via terminal.
Currently this uses simple communication via sockets and data pickling and fixed generalization hierarchies.
"""
import argparse
import json
from operator import itemgetter
from typing import Any, List
from timeit import default_timer as timer
from datetime import timedelta

import adult_data
import medical_data
from src.motion import Party
from src.central import Central
from src.communication import receive_data
from src.constants import DATA_ROWS, INFO
from src.counter_information_data import CounterInformationData


DEFAULT_K = 5
DEFAULT_NUMBER_OF_BOXES = 3
DEFAULT_HOST = "127.0.0.1"
DEFAULT_RING_PORT = 4442
DEFAULT_MOTION_PORT = 5442


def ask_for_criteria():
    temp_criteria_list = []
    criterion = input("\nEnter criterion, e.g. Age < 65: ")
    while criterion != "":
        criterion_split = criterion.split(" ")
        if len(criterion_split) != 3:
            print("Error: criterion must be of format '<category> <comparison operator> <value>")
            break
        elif criterion_split[1] != "=" and criterion_split[1] != "<" and criterion_split[1] != ">":
            print("\nError: I only know comparison operators =, < and >.")
            print("You provided: " + criterion_split[1])
            break

        temp_criteria_list.append(criterion_split)

        criterion = input("\n\nMore criteria? If yes, type criteria. Otherwise just Enter. ")
    return temp_criteria_list


def run_request(k: int, criteria_list: List, parties, central_host, central_ring_port, central_motion_port, qid_attribute_trees) -> List[List[Any]]:
    """
    Perform the required steps in the distributed algorithm to compute a request result.

    :param k: the parameter for the anonymity metric
    :param criteria_list: criteria for the request
    :param : TODO
    :return: the anonymized result data
    """
    c = Central(k, qid_attribute_trees, criteria_list, parties, central_host, central_ring_port, central_motion_port)

    # run initial round
    c.start_initial_round()

    response = receive_data(central_host, central_ring_port)
    counter_information: CounterInformationData = response[INFO]

    c.complete_round(counter_information)

    # perform rounds as long as further refinements are possible
    while c.can_perform_round():
        c.start_round()

        response = receive_data(central_host, central_ring_port)
        blinded_counter_information: CounterInformationData = response[INFO]

        c.complete_round(blinded_counter_information)

    # final secure set union
    c.start_secure_data_union()

    response = receive_data(central_host, central_ring_port)
    encrypted_result = response[DATA_ROWS]

    anonymized_result = c.complete_secure_data_union(encrypted_result)
    return anonymized_result


def print_results(data_rows):
    print("\nResult: ")
    for row in data_rows:
        print("  " + json.dumps(row))
    print("(" + str(len(data_rows)) + " rows.)")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--number_of_boxes', type=int, help='Number of participating boxes.', default=DEFAULT_NUMBER_OF_BOXES)
    parser.add_argument('--address', help='The central ip address.', default=DEFAULT_HOST)
    parser.add_argument('--ringport', type=int, help='The central port for ring communication.', default=DEFAULT_RING_PORT)
    parser.add_argument('--motionport', type=int, help='The central port for MOTION communication.', default=DEFAULT_MOTION_PORT)
    parser.add_argument('--anonymity_parameter', type=int, help='The anonymity parameter k of k-anonymity.', default=DEFAULT_K)
    parser.add_argument('--interactive_criteria', action='store_true', help='If set, criteria can be set interactively.')
    parser.add_argument('--dataset', help='The data set to be used ([medical]/adult).', choices=["adult", "medical"], default="medical")
    parser.add_argument('--used_qids', help='Comma-separated list, can be used to restrict the used QIDs.')
    args = parser.parse_args()

    number_of_boxes = args.number_of_boxes
    # TODO this sets the default address and ports for all boxes, changes are not possible atm
    parties = [Party(i, "127.0.0.1", 4442 + i, 5442 + i) for i in range(1, number_of_boxes + 1)]

    central_host = args.address
    central_ring_port = args.ringport
    central_motion_port = args.motionport
    k = args.anonymity_parameter

    print(f"Starting central server [Number of boxes: {number_of_boxes}, dataset: {args.dataset}, k: {k}]", flush=True)

    all_qid_attribute_trees = medical_data.attribute_trees if args.dataset == "medical" else adult_data.attribute_trees
    used_qids_arg = args.used_qids
    if used_qids_arg:
        used_qids = [int(q.strip()) for q in used_qids_arg.split(",")]
        used_qid_attribute_trees = {k: v for k, v in all_qid_attribute_trees.items() if k in used_qids}
        if len(used_qid_attribute_trees) != len(used_qids):
            raise ValueError(f"{used_qids} as QIDs requested, but there only exist the following QIDs: {list(all_qid_attribute_trees.keys())}")
    else:
        used_qid_attribute_trees = all_qid_attribute_trees
    num_qids = len(used_qid_attribute_trees)

    print(f"Starting central server [Number of boxes: {number_of_boxes}, dataset: {args.dataset}, k: {k}, num_qids: {num_qids}]", flush=True)
    used_qids_output_str = ','.join(map(str, list(used_qid_attribute_trees.keys())))
    print(f"Used QIDs: {used_qids_output_str}", flush=True)

    criteria_list = []
    if args.interactive_criteria:
        criteria_list = ask_for_criteria()
    
    start = timer()

    anonymized_result = run_request(k, criteria_list, parties, central_host, central_ring_port, central_motion_port, used_qid_attribute_trees)

    end = timer()

    print(f"FINISHED - time elapsed [{timedelta(seconds=end-start)}]")

    sorted_anon_result = sorted(anonymized_result, key=itemgetter(1))
    print_results(sorted_anon_result)


if __name__ == "__main__":
    main()
