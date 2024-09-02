#/bin/env python3

import logging
import glob 
from pprint import pprint
from collections import defaultdict
import operator

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


def seconds_from_time(time_str):
    h, m, s = time_str.split(':')
    return int(h) * 3600 + int(m) * 60 + float(s)



def evaluate(filename: str):
    with open(filename) as f:
        evalinput = [l.strip() for l in f]

    # parse network before
    # NETWORK BEFORE: {'lo': snetio(bytes_sent=1166757099, bytes_recv=1166757099, packets_sent=1688496, packets_recv=1688496, errin=0, errout=0, dropin=0, dropout=0), 'en0': snetio(bytes_sent=67556628, bytes_recv=1411099, packets_sent=140183, packets_recv=16237, errin=0, errout=0, dropin=0, dropout=0), 'en1': snetio(bytes_sent=7331181, bytes_recv=110440701, packets_sent=75314, packets_recv=120873, errin=0, errout=0, dropin=0, dropout=0)}
    network_str = evalinput[0]
    NETWORK_BEFORE_START = "NETWORK BEFORE:"

    if not network_str.startswith(NETWORK_BEFORE_START):
        raise ValueError(f"Invalid input file line: Expected {NETWORK_BEFORE_START} {network_str}")

    dict_str = network_str[16:]

    # really hacky, but hey, it's an evaluation script 
    snetio = dict
    network_before = eval(dict_str)
    bytes_sent_before = network_before['lo']['bytes_sent']
    bytes_recv_before = network_before['lo']['bytes_recv']


    # parse eval parameters
    # Starting central server [Number of boxes: 3, dataset: adult, k: 5]
    param_str = evalinput[2]
    if not param_str.startswith("Starting central server ["):
        raise ValueError("Invalid input file")

    param_str = param_str.split("[")[1][:-1]
    params = param_str.split(", ")
    num_boxes = int(params[0].split(": ")[1])
    dataset = params[1].split(": ")[1]
    k = int(params[2].split(": ")[1])
    num_qids = int(params[3].split(": ")[1])

    # parse qids
    qid_str = evalinput[3]
    if not qid_str.startswith("Used QIDs: "):
        raise ValueError("Invalid input file, expected 'Used QIDs: '")
    used_qids = qid_str[11:]

    # parse motion lines
    MOTION_STATISTICS_SEPARATOR = "==========================================================================="
    PREPROCESSING_LINE_START = "Preprocessing Total"
    CIRCUIT_EVAL_LINE_START = "Circuit Evaluation"
    DATA_SENT_LINE_START = "Sent:"

    FINAL_TIME_LINE_START = "FINISHED"

    motion_runs = []

    ln = 4
    number_of_rounds = 0
    while ln < len(evalinput):
        current_line = evalinput[ln]

        if current_line == MOTION_STATISTICS_SEPARATOR:
            # MOTION LINES
            """
===========================================================================
Statistics
===========================================================================
MOTION version: 96f1c1d-dirty @ panda
invocation: python /export2/home/petersen/infhome/git/panda-code/run_central.py --number_of_boxes 3 --dataset adult
by petersen@ccblade3, PID 445008
===========================================================================
Run time statistics over 1 iterations
---------------------------------------------------------------------------
                          mean        median        stddev
---------------------------------------------------------------------------
MT Presetup              0.574 ms      0.000 ms -nan       ms
MT Setup               106.238 ms      0.000 ms      0.000 ms
SP Presetup              0.000 ms      0.000 ms      0.000 ms
SP Setup                 0.000 ms      0.000 ms      0.000 ms
SB Presetup              0.000 ms      0.000 ms      0.000 ms
SB Setup                 0.000 ms      0.000 ms      0.000 ms
Base OTs               237.074 ms      0.000 ms      0.000 ms
OT Extension Setup      43.758 ms      0.000 ms -nan       ms
---------------------------------------------------------------------------
Preprocessing Total    390.200 ms      0.000 ms -nan       ms
Gates Setup              0.000 ms      0.000 ms      0.000 ms
Gates Online             0.000 ms      0.000 ms      0.000 ms
---------------------------------------------------------------------------
Circuit Evaluation     839.181 ms      0.000 ms      0.000 ms
===========================================================================
Communication with each other party:
Sent: 1.136 MiB in 8983 messages
Received: 1.136 MiB in 8983 messages
===========================================================================
            """

            # preprocessing time
            logging.debug("FOUND motion line", ln)

            preprocessing_line = evalinput[ln + 20]
            if not PREPROCESSING_LINE_START in preprocessing_line:
                raise ValueError(f"Expected preprocessing line, found {preprocessing_line} [L. {ln + 20}]")

            preprocessing_time = float(preprocessing_line.split()[2])

            # circuit eval time
            circuit_eval_line = evalinput[ln + 24]
            if not CIRCUIT_EVAL_LINE_START in circuit_eval_line:
                raise ValueError(f"Expected circuit eval line, found {circuit_eval_line} [L. {ln + 24}]")

            circuit_eval_time = float(circuit_eval_line.split()[2])

            # data sent time
            sent_line = evalinput[ln + 27]
            if not DATA_SENT_LINE_START in sent_line:
                raise ValueError(f"Expected sent line, found {sent_line} [L. {ln + 27}]")

            messages_sent = int(sent_line.split()[4].replace(".", ""))
            messages_sent_size = float(sent_line.split()[1])

            run = {
                "preprocessing": preprocessing_time,
                "circuit_eval": circuit_eval_time,
                "messages": messages_sent,
                "messages_size": messages_sent_size
            }

            motion_runs.append(run)

            logging.debug("\n".join(evalinput[ln:ln+30]))
            logging.debug(run)

            ln += 30
        elif "Next best refinement" in current_line:
            number_of_rounds += 1
            ln += 1
        elif FINAL_TIME_LINE_START in current_line:
            # parse final time line
            # FINISHED - time elapsed [0:05:38.568103]
            logging.debug("FOUND FINAL LINE", ln)
            final_time = current_line.split("[")[1][:-1]
            seconds = seconds_from_time(final_time)
            break
        else:
            ln += 1
        
    motion_messages = sum([r["messages"] for r in motion_runs])
    motion_messages_size = sum([r["messages_size"] for r in motion_runs])
    motion_preprocessing = sum([r["preprocessing"] for r in motion_runs]) / 1000  # ms to s 
    motion_circuit_eval = sum([r["circuit_eval"] for r in motion_runs]) / 1000  # ms to s

    # final networking line
    # 
    network_str = evalinput[-1]
    if not network_str.startswith("NETWORK AFTER:"):
        raise ValueError("Invalid input file")

    dict_str = network_str[15:]

    # really hacky, but hey, it's an evaluation script 
    snetio = dict
    network_after= eval(dict_str)
    bytes_sent_after= network_after['lo']['bytes_sent']
    bytes_recv_after= network_after['lo']['bytes_recv']


    return {
            "dataset": dataset,
            "k": k,
            "num_boxes": num_boxes,
            "num_qids": num_qids,
            "used_qids": used_qids,
            "rounds": number_of_rounds,
            "required_time": seconds,
            "motion_messages": motion_messages,
            "motion_messages_size": motion_messages_size,
            "motion_preprocessing": motion_preprocessing,
            "motion_circuit_eval": motion_circuit_eval,
            "lo_bytes_sent_before": bytes_sent_before,
            "lo_bytes_sent_after": bytes_sent_after,
            "lo_bytes_sent": bytes_sent_after - bytes_sent_before,
            "lo_bytes_recv": bytes_recv_after - bytes_recv_before,
    }


def main():
    path_runs_motion = "./ccblade_bak/runs_arb_qid_motion/*.txt"
    path_runs_securesum = "./ccblade_bak/runs_arb_qid_securesum/*.txt"

    motion_runs = defaultdict(dict)
    for file in glob.glob(path_runs_motion):
        run = evaluate(file)
        motion_runs[run["dataset"]][run["used_qids"]] = run

    securesum_runs = defaultdict(dict)
    for file in glob.glob(path_runs_securesum):
        run = evaluate(file)
        securesum_runs[run["dataset"]][run["used_qids"]] = run

   #  print("=" * 10, "MOTION", "=" * 10)
   #  pprint(motion_runs)
   #  print("=" * 10, "SECURE_SUM", "=" * 10)
   #  pprint(securesum_runs)
    
    OUR_PROTOCOL_TITLE = "our protocol" 
    ORIGINAL_PROTOCOL_TITLE = "Mohammed et al."
 
    methods = [OUR_PROTOCOL_TITLE for _ in range(len(motion_runs) * len(motion_runs["adult"]))] + [ORIGINAL_PROTOCOL_TITLE for _ in range(len(securesum_runs) * len(securesum_runs["adult"]))]

    def all_field_values(field: str):
        result = [run[field] for runs in motion_runs.values() for run in runs.values()] + [run[field] for runs in securesum_runs.values() for run in runs.values()]
        return result

    motion_mib_bytes = list(map(lambda v: v[0] * v[1]  * v[1], zip(all_field_values("motion_messages_size"), all_field_values("num_boxes"))))
    motion_bytes = list(map(lambda v: v * (2 ** 20), motion_mib_bytes))
    motion_times = list(map(lambda v: v[0] + v[1], zip(all_field_values("motion_circuit_eval"), all_field_values("motion_preprocessing"))))
    mib_bytes = list(map(lambda v: v / (2 ** 20), all_field_values("lo_bytes_sent")))

    df = pd.DataFrame({
        "dataset": all_field_values("dataset"),
        "method": methods,
        "num_boxes": all_field_values("num_boxes"),
        "num_qids": all_field_values("num_qids"),
        "used_qids": all_field_values("used_qids"),
        "rounds": all_field_values("rounds"),
        "time": all_field_values("required_time"),
        "bytes": all_field_values("lo_bytes_sent"),
        # "mib_bytes": mib_bytes,
        # "motion_bytes": motion_bytes,
        # "motion_mib_bytes": motion_mib_bytes,
        # "motion_times": motion_times,
    })

    df.sort_values(by=["dataset", "method", "time"], inplace=True)

    print(df.to_string())

    # seaborn config

    # sns.set_style("ticks")
    # sns.despine()
    # sns.set_style("whitegrid")
    sns.set_theme("paper")

    plt.tight_layout()
    
    ADJUST_KEYS = {
        "left": 0.07, 
        "bottom": 0.16, 
        "right": 1, 
        "top":0.97 
    }
    # we have to provide the order of qids sorted by time for our protocol, otherwise Mohammed order is used
    x_sort_order = df[len(motion_runs["adult"]):].used_qids.tolist()

    # FIGURE 1 
    # line_chart
    # SECURESUM, MOTION
    # num_qids -> time

    fig, axs = plt.subplots(figsize=[10, 6])
    sns.barplot(
            data=df, 
            x="used_qids", 
            y="time", 
            hue="method", 
            ax=axs,
            order=x_sort_order
    )
    plt.setp(axs.get_xticklabels(), rotation=90)
    axs.set_ylabel('time [s]')
    axs.set_xlabel('used QID set')
    axs.legend().set_title(None)
    fig.subplots_adjust(**ADJUST_KEYS)
    fig.savefig("img/arb_qid_adult_time_bar.png")

    # DO NOT SORT FOR BETTER COMPARABILITY
    # df.sort_values(by=["dataset", "method", "bytes"], inplace=True)

    # FIGURE 3
    # line_chart
    # SECURESUM, MOTION
    # num_qids -> bytes 
    
    fig, axs = plt.subplots(figsize=[10, 6])
    sns.barplot(
            data=df, 
            x="used_qids", 
            y="bytes", 
            hue="method", 
            ax=axs, 
            order=x_sort_order
    )
    plt.setp(axs.get_xticklabels(), rotation=90)
    axs.set_ylabel('sent data [byte]')
    axs.set_xlabel('used QID set')
    axs.legend().set_title(None)
    fig.subplots_adjust(**ADJUST_KEYS)
    fig.savefig("img/arb_qid_adult_bytes_bar.png")
    
if __name__ == "__main__":
    main()
