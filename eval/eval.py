# /bin/env python3

import logging
import glob
from pprint import pprint
from collections import defaultdict
import operator

import pandas as pd
import seaborn as sns
import numpy as np
import matplotlib.pyplot as plt

# NETWORK output example - one line in the logfile
"""
NETWORK BEFORE: {
    'lo': snetio(bytes_sent=292332595728, bytes_recv=292332595728, packets_sent=146781745, packets_recv=146781745, errin=0, errout=0, dropin=0, dropout=0), 
    'eno1': snetio(bytes_sent=37011496728, bytes_recv=354135665856, packets_sent=48611883, packets_recv=246648553, errin=0, errout=0, dropin=473596, dropout=0), 
    'eno2': snetio(bytes_sent=0, bytes_recv=0, packets_sent=0, packets_recv=0, errin=0, errout=0, dropin=0, dropout=0)
}
"""

# MOTION statistics example for documentation purposes
"""
===========================================================================
Statistics
===========================================================================
MOTION version: 5e0b8ee-dirty @ panda-new
invocation: python ../ours/run_central.py --number_of_boxes 3 --dataset medical
by petersen@ccblade4, PID 759499
===========================================================================
Run time statistics over 1 iterations
---------------------------------------------------------------------------
                          mean        median        stddev
---------------------------------------------------------------------------
MT Presetup             14.254 ms      0.000 ms -nan       ms
MT Setup                14.831 ms      0.000 ms      0.000 ms
SP Presetup              0.000 ms      0.000 ms      0.000 ms
SP Setup                 0.000 ms      0.000 ms      0.000 ms
SB Presetup              0.000 ms      0.000 ms      0.000 ms
SB Setup                 0.000 ms      0.000 ms      0.000 ms
Base OTs                 0.000 ms      0.000 ms      0.000 ms
OT Extension Setup      37.994 ms      0.000 ms      0.000 ms
KK13 OT Extension Setup      0.000 ms      0.000 ms      0.000 ms
---------------------------------------------------------------------------
Preprocessing Total    214.407 ms      0.000 ms      0.000 ms
Gates Setup              0.000 ms      0.000 ms      0.000 ms
Gates Online             0.000 ms      0.000 ms      0.000 ms
---------------------------------------------------------------------------
Circuit Evaluation     926.460 ms      0.000 ms      0.000 ms
===========================================================================
Communication with each other party:
Sent: 0.387 MiB in 3969 messages
Received: 0.387 MiB in 3969 messages
===========================================================================
            """


PATH_RUNS_MOTION = "./data/runs_motion/*.txt"
PATH_RUNS_SECURESUM = "./data/runs_securesum/*.txt"

OUR_PROTOCOL_TITLE = "Our protocol"
ORIGINAL_PROTOCOL_TITLE = "Mohammed et al."


def seconds_from_time(time_str):
    h, m, s = time_str.split(':')
    return int(h) * 3600 + int(m) * 60 + float(s)


def parse_file(filename: str):
    with open(filename) as f:
        filecontent = [l.strip() for l in f]

    # parse network before
    # example see above
    network_str = filecontent[0]
    NETWORK_BEFORE_START = "NETWORK BEFORE:"

    if not network_str.startswith(NETWORK_BEFORE_START):
        raise ValueError(f"Invalid input file line: Expected {NETWORK_BEFORE_START} {network_str}")

    dict_str = network_str[16:]

    # really hacky, but hey, it's an evaluation script 
    # snetio is part of the network output and followed by params. making it a alias for dict allows for direct eval
    snetio = dict
    network_before = eval(dict_str)
    bytes_sent_before = network_before['lo']['bytes_sent']
    bytes_recv_before = network_before['lo']['bytes_recv']

    # parse eval parameters
    # Example: Starting central server [Number of boxes: 3, dataset: adult, k: 5]
    param_str = filecontent[1]
    if not param_str.startswith("Starting central server ["):
        raise ValueError("Invalid input file")

    param_str = param_str.split("[")[1][:-1]
    params = param_str.split(", ")
    num_boxes = int(params[0].split(": ")[1])
    dataset = params[1].split(": ")[1]
    k = int(params[2].split(": ")[1])

    # parse motion lines
    MOTION_STATISTICS_SEPARATOR = "==========================================================================="
    PREPROCESSING_LINE_START = "Preprocessing Total"
    CIRCUIT_EVAL_LINE_START = "Circuit Evaluation"
    DATA_SENT_LINE_START = "Sent:"
    FINAL_TIME_LINE_START = "FINISHED"
    MOTION_STATISTICS_LINE_LEN = 31

    motion_runs = []

    ln = 2
    while ln < len(filecontent):
        current_line = filecontent[ln]

        if current_line == MOTION_STATISTICS_SEPARATOR:
            # MOTION LINES, examples see top of file

            # preprocessing time
            logging.debug("FOUND motion line", ln)

            preprocessing_line = filecontent[ln + 21]
            if not PREPROCESSING_LINE_START in preprocessing_line:
                raise ValueError(f"Expected preprocessing line, found {preprocessing_line} [L. {ln + 21}] in {filename}")

            preprocessing_time = float(preprocessing_line.split()[2])

            # circuit eval time
            circuit_eval_line = filecontent[ln + 25]
            if not CIRCUIT_EVAL_LINE_START in circuit_eval_line:
                raise ValueError(f"Expected circuit eval line, found {circuit_eval_line} [L. {ln + 25}]")

            circuit_eval_time = float(circuit_eval_line.split()[2])

            # data sent time
            sent_line = filecontent[ln + 28]
            if not DATA_SENT_LINE_START in sent_line:
                raise ValueError(f"Expected sent line, found {sent_line} [L. {ln + 28}]")

            messages_sent = int(sent_line.split()[4].replace(".", ""))
            messages_sent_size = float(sent_line.split()[1])

            run = {
                "preprocessing": preprocessing_time,
                "circuit_eval": circuit_eval_time,
                "messages": messages_sent,
                "messages_size": messages_sent_size
            }

            motion_runs.append(run)

            logging.debug("\n".join(filecontent[ln:ln + MOTION_STATISTICS_LINE_LEN]))
            logging.debug(run)

            ln += MOTION_STATISTICS_LINE_LEN
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
    network_str = filecontent[-1]
    if not network_str.startswith("NETWORK AFTER:"):
        raise ValueError("Invalid input file")

    dict_str = network_str[15:]

    # really hacky, but hey, it's an evaluation script 
    snetio = dict
    network_after = eval(dict_str)
    bytes_sent_after = network_after['lo']['bytes_sent']
    bytes_recv_after = network_after['lo']['bytes_recv']

    return {
        "file": filename,
        "dataset": dataset,
        "k": k,
        "num_boxes": num_boxes,
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


def parse_runs():
    runs = []

    for file in glob.glob(PATH_RUNS_MOTION):
        run = parse_file(file)
        run["protocol"] = OUR_PROTOCOL_TITLE
        runs.append(run)

    for file in glob.glob(PATH_RUNS_SECURESUM):
        run = parse_file(file)
        run["protocol"] = ORIGINAL_PROTOCOL_TITLE
        runs.append(run)

    return runs


def create_raw_dataframe(runs):
    df = pd.DataFrame(runs)

    MIB_BYTES_FACTOR = 2 ** 20

    df["time"] = df["required_time"]
    df["bytes"] = df["lo_bytes_sent"]
    df["time_party"] = df["required_time"] / df["num_boxes"]
    df["motion_times"] = df["motion_circuit_eval"] + df["motion_preprocessing"]
    df["mib_bytes"] = df["bytes"] / MIB_BYTES_FACTOR
    df["bytes_party"] = df["bytes"] / df["num_boxes"]
    df["mib_bytes_party"] = df["mib_bytes"] / df["num_boxes"]
    df["motion_mib_bytes"] = df["motion_messages_size"] * df["num_boxes"]
    df["motion_bytes"] = df["motion_mib_bytes"] * MIB_BYTES_FACTOR

    df = df.sort_values(by=["dataset", "num_boxes", "protocol"])

    return df


def create_aggregated_dataframe(df):
    result = df\
        .groupby(["dataset", "protocol", "num_boxes"], as_index=False, sort=False)\
        .agg(time_mean=("time", "mean"),
             time_std=("time", "std"),
             bytes_mean=("bytes", "mean"),
             bytes_std=("bytes", "std"),
             mib_bytes_mean=("mib_bytes", "mean"),
             mib_bytes_std=("mib_bytes", "std"),
             )
    return result


def create_figure(ours_data: pd.DataFrame, original_data: pd.DataFrame, mean_field: str, std_field: str, ylabel: str, figure_path: str):
    ADJUST_KEYS = {
        "left": 0.12,
        "bottom": 0.1,
        "right": 1,
        "top": 0.95
    }

    fig, axs = plt.subplots()
    x = np.arange(len(ours_data))
    width = 0.3
    bar = axs.errorbar(x=ours_data["num_boxes"],
                       y=ours_data[mean_field],
                       yerr=ours_data[std_field],
                       label=OUR_PROTOCOL_TITLE,
                       fmt=".-")
    bar = axs.errorbar(x=original_data["num_boxes"],
                       y=original_data[mean_field],
                       yerr=original_data[std_field],
                       label=ORIGINAL_PROTOCOL_TITLE,
                       fmt=".-")
    axs.set_ylabel(ylabel)
    axs.set_xlabel('number of parties')
    axs.legend().set_title(None)
    fig.subplots_adjust(**ADJUST_KEYS)
    fig.savefig(figure_path, dpi=600)


def draw_images(df: pd.DataFrame):
    adult_data = df[(df["dataset"] == "adult")]
    adult_ours_data = df[(df["dataset"] == "adult") & (df["protocol"] == OUR_PROTOCOL_TITLE)]
    adult_original_data = df[(df["dataset"] == "adult") & (df["protocol"] == ORIGINAL_PROTOCOL_TITLE)]
    # print(adult_data)

    medical_data = df[(df["dataset"] == "medical")]
    medical_ours_data = df[(df["dataset"] == "medical") & (df["protocol"] == OUR_PROTOCOL_TITLE)]
    medical_original_data = df[(df["dataset"] == "medical") & (df["protocol"] == ORIGINAL_PROTOCOL_TITLE)]
    # print(medical_data)

    sns.set_theme("paper")

    # FIGURE 1 
    # ADULT
    # line_chart
    # SECURESUM, MOTION
    # num_boxes -> time
    create_figure(adult_ours_data, adult_original_data, "time_mean", "time_std", "time [s]", "img/adult_time.png")

    # FIGURE 2
    # MEDICAL
    # line_chart
    # SECURESUM, MOTION
    # num_boxes -> time
    create_figure(medical_ours_data, medical_original_data, "time_mean", "time_std", "time [s]", "img/medical_time.png")

    # FIGURE 3
    # MEDICAL
    # line_chart
    # SECURESUM, MOTION
    # num_boxes -> bytes
    create_figure(medical_ours_data, medical_original_data, "bytes_mean", "bytes_std", "sent data [byte]", "img/medical_bytes.png")
    create_figure(medical_ours_data, medical_original_data, "mib_bytes_mean", "mib_bytes_std", "sent data [MiB]", "img/medical_mib_bytes.png")

    # FIGURE 4
    # ADULT
    # line_chart
    # SECURESUM, MOTION
    # num_boxes -> bytes
    create_figure(adult_ours_data, adult_original_data, "bytes_mean", "bytes_std", "sent data [byte]", "img/adult_bytes.png")
    create_figure(adult_ours_data, adult_original_data, "mib_bytes_mean", "mib_bytes_std", "sent data [MiB]", "img/adult_mib_bytes.png")


def render_latex_table(df):
    # create and print LaTeX table rows like the following
    # medical & 2 & & 0.6 s & 75.1 s & & 0.8 MB & 80.9 MB\\

    def byte_repr(inbytes):
        if inbytes > 10 ** 9:
            result = "{:.2f} GB".format(inbytes / (10 ** 9))
        else:
            result = "{:.0f} MB".format(inbytes / (10 ** 6))
        return result

    # we combine two adjacent rows to tranform them into one table row (original vs. our protocol)
    df_tuples = list(enumerate(df.itertuples(index=False)))
    df_zipped_tuples = list(zip([row for i, row in df_tuples if i % 2 == 0], [row for i, row in df_tuples if i % 2 == 1]))

    current_dataset = ""  # used to populate only the first dataset row
    for mohammed_row, our_row in df_zipped_tuples:
        assert mohammed_row.dataset == our_row.dataset
        assert mohammed_row.num_boxes == our_row.num_boxes

        if our_row.dataset != current_dataset:
            current_dataset = our_row.dataset
            dataset = our_row.dataset
        else:
            dataset = ""

        num_boxes = our_row.num_boxes
        time_our = "{:.1f} s".format(our_row.time_mean)
        time_mohammed = "{:.1f} s".format(mohammed_row.time_mean)
        bytes_our = our_row.bytes_mean
        bytes_mohammed = mohammed_row.bytes_mean
        byte_repr_our = byte_repr(bytes_our)
        byte_repr_mohammed = byte_repr(bytes_mohammed)
        latex_row = f"{dataset} & {num_boxes} & & {time_mohammed} & {time_our} & & {byte_repr_mohammed} & {byte_repr_our} \\\\"
        print(latex_row)


def main():
    runs = parse_runs()
    # pprint(runs)

    df = create_raw_dataframe(runs)
    #print(df.to_string())

    df_agg = create_aggregated_dataframe(df)
    print(df_agg.to_string())

    draw_images(df_agg)
    render_latex_table(df_agg)


if __name__ == "__main__":
    main()
