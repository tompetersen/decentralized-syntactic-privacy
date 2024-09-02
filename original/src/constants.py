from enum import IntEnum
from typing import List, Any, Dict


# constants for dummies used in secure set union

DUMMY = "DUMMY"
NR_DUMMIES_MAX = 50
NR_DUMMIES_MIN = 1
DUMMY_ROW = [1, 99, 1, 1.0, 1.0, 0, 0, 1.0, 0.0, 0.0, 0.0, 1, 0, 8.0, 1.0, 3.0, 1, 6.0, 1.0, 6.0]

# constants and types for communication

CENTRAL_PK = "central_pk"
CRITERIA = "criteria"
REQUEST_TYPE = "request_type"
INFO = "info"
QID_ATTRIBUTE_TREES = "qid_attribute_trees"
BEST_REFINEMENTS = "best_refinements"
BEST_ATTRIBUTE_INDEX = "best_attribute_index"
BEST_LABEL = "best_label"
DATA_ROWS = "data_rows"
PARTIES = "parties"


class RequestType(IntEnum):
    INFORMATION = 1
    INSTRUCTION = 2
    END = 3


# Supporting types placed here to prevent circular imports occuring otherwise

AttributeIndex = int

GeneralizationLabel = str

TipsNodeId = str

Data = List[List[Any]]

EncryptedData = List[bytes]

BestRefinements = Dict[TipsNodeId, AttributeIndex]
