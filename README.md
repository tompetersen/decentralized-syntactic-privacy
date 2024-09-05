# Readme

This repository contains our code for a distributed syntactic privacy protocol presented by Mohammed et al. at TKDD2010
(Mohammed et al. Centralized and Distributed Anonymization for High-Dimensional Healthcare Data. https://doi.org/10.1145/1857947.1857950)
as well as the code for our improved protocol variant which addresses weaknesses in the original protocol.
The improved variant makes use of the SMPC framework MOTION (https://github.com/encryptogroup/MOTION).

Running the protocol requires building a MOTION-based library. Necessary steps are detailed below.

## Build MOTION pandapython lib

- Checkout the repository https://github.com/tompetersen/MOTION and switch to branch `panda`.
-  Follow MOTION build steps detailed in their README.
-  Call cmake with `-DMOTION_BUILD_EXE=On`: `$ cmake .. -DMOTION_BUILD_EXE=On`
-  If successful, `build/lib` should contain the library `pandapython.*.so`.

## Create environment variable for lib path

-  Create an environment variable for this path: `$ export MOTION_PANDA_LIB_PATH=/path/to/motion/build/lib/`

## Setup venv

- Setup your python venv and install requirements
  - `$ python3 -m venv venv`
  - `$ . venv/bin/activate`
  - `$ pip install -r ours/requirements.txt`

## Evaluation

- To compare the performance of our vs. the original protocol
  - `$ pip install -r eval/requirements.txt`
  - `$ ./run.sh`
  - This creates eval files in `eval/data/...`
  - `$ python eval.py` creates figures in `img` and outputs LaTeX table content
- To show the influence of various QID combinations
  - `$./run_arb_qid.sh` creates eval files in `eval/data/...`
  - `$ python eval_arb_qid.sh` creates figures
- `run.sh` is also a good starting point for running the protocol yourself manually

# Test datasets

- There are two datasets used in the evaluation currently
  - ADULT: The famous Census Income dataset (https://doi.org/10.24432/C5XW20)
  - Medical: A synthetically generated dataset containing some QIDs and additional medical markers.