#!python3

import psutil
from pprint import pprint


network = psutil.net_io_counters(pernic=True)

for adapter, stats in network.items():
    print(f"\n{adapter}")
    pprint(stats)
