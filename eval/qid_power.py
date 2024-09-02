#!/usr/bin/env python3

import more_itertools

# already successfully performed some eval runs? and then the machine went crazy? no worries...
FIRST = "0"

qids = [0, 4, 5, 6, 8, 9]
result = list(more_itertools.powerset(qids))[1:]
results = list(map(lambda t: ",".join(map(str, t)), result))
results = results[results.index(FIRST):]
result_str = ' '.join(results)
print(result_str)
