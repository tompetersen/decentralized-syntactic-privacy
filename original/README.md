# PANDA test environment for the k-anonymization of medical data

The anonymization algorithm implements the approach in [1].

## Setup:
* create virtual environment in `panda-code/venv`
    * (or somewhere else, remember to change the reference in `panda-run` accordingly)
* `pip install -r requirements.txt`

## Run:
1. Run `panda-run <Anzahl der Epp-Boxen>` on the console for an interactive execution. Uses the patient metadata modelled by eppdata. 
**Output:** The k-anonymized dataset.
2. Run the following files for a quick, non-interactive execution. The configuration (e.g. the value of `k`) may be changed by editing the files. 
**Output:** Basic statistical insight into the k-anonymized dataset.
    * `run_medical.py`: Uses the modelled metadata by eppdata (~2.4k data rows)
    * `run_adult.py`: Uses the [ADULT data set](http://archive.ics.uci.edu/ml/datasets/Adult), compromising ~48k data rows.

## Test

`python -m unittest discover tests`

### Changelog
[0.4](https://git.informatik.uni-hamburg.de/svs/panda-code/-/tags/0.4): Refactored and clean code. Introduces ADULT dataset. Implements Secure Set Union in last round.

[0.3](https://git.informatik.uni-hamburg.de/svs/panda-code/-/tags/0.3): Decentralized (distributed) algorithm [1, Section 5]

[0.2](https://git.informatik.uni-hamburg.de/svs/panda-code/-/tags/0.2): Uses TIPS-trees to increase performance [1, Def. 4.1]

[0.1](https://git.informatik.uni-hamburg.de/svs/panda-code/-/tags/0.1): Centralized approach without performance optimizations 

### References
[[1](https://doi.org/10.1145/1857947.1857950)], [pdf](https://dl.acm.org/doi/pdf/10.1145/1857947.1857950): Noman Mohammed, Benjamin C. M. Fung, Patrick C. K. Hung, and Cheuk-Kwong Lee. 2010. Centralized and Distributed Anonymization for High-Dimensional Healthcare Data. ACM Trans. Knowl. Discov. Data 4, 4, Article 18 (October 2010), 33 pages.