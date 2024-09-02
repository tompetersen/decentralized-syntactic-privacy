import os

from src.qid_hierarchy_node import NumericalQidHierarchyNode


# hierarchies


def get_sex_tree() -> NumericalQidHierarchyNode:
    sex_root = NumericalQidHierarchyNode(min=1, max=2)
    sex_0 = NumericalQidHierarchyNode(parent=sex_root, min=1, max=1)
    sex_1 = NumericalQidHierarchyNode(parent=sex_root, min=2, max=2)
    return sex_root


def get_age_tree() -> NumericalQidHierarchyNode:
    age_root = NumericalQidHierarchyNode(min=1, max=119)
    age_0 = NumericalQidHierarchyNode(parent=age_root, min=1, max=76)
    age_0_0 = NumericalQidHierarchyNode(parent=age_0, min=1, max=65)
    age_0_0_0 = NumericalQidHierarchyNode(parent=age_0_0, min=1, max=57)
    age_0_0_0_0 = NumericalQidHierarchyNode(parent=age_0_0_0, min=1, max=30)
    age_0_0_0_0_0 = NumericalQidHierarchyNode(parent=age_0_0_0_0, min=1, max=25)
    age_0_0_0_0_1 = NumericalQidHierarchyNode(parent=age_0_0_0_0, min=26, max=30)
    age_0_0_0_1 = NumericalQidHierarchyNode(parent=age_0_0_0, min=31, max=50)
    age_0_0_0_1_0 = NumericalQidHierarchyNode(parent=age_0_0_0_1, min=31, max=40)
    age_0_0_0_1_0_0 = NumericalQidHierarchyNode(parent=age_0_0_0_1_0, min=31, max=35)
    age_0_0_0_1_0_1 = NumericalQidHierarchyNode(parent=age_0_0_0_1_0, min=36, max=40)
    age_0_0_0_1_1 = NumericalQidHierarchyNode(parent=age_0_0_0_1, min=41, max=50)
    age_0_0_0_1_1_0 = NumericalQidHierarchyNode(parent=age_0_0_0_1_1, min=41, max=46)
    age_0_0_0_1_1_0_0 = NumericalQidHierarchyNode(parent=age_0_0_0_1_1_0, min=41, max=44)
    age_0_0_0_1_1_0_1 = NumericalQidHierarchyNode(parent=age_0_0_0_1_1_0, min=45, max=46)
    age_0_0_0_1_1_1 = NumericalQidHierarchyNode(parent=age_0_0_0_1_1, min=47, max=50)
    age_0_0_0_2 = NumericalQidHierarchyNode(parent=age_0_0_0, min=51, max=57)
    age_0_0_0_2_0 = NumericalQidHierarchyNode(parent=age_0_0_0_2, min=51, max=54)
    age_0_0_0_2_0_0 = NumericalQidHierarchyNode(parent=age_0_0_0_2_0, min=51, max=52)
    age_0_0_0_2_0_0_0 = NumericalQidHierarchyNode(parent=age_0_0_0_2_0_0, min=51, max=51)
    age_0_0_0_2_0_0_1 = NumericalQidHierarchyNode(parent=age_0_0_0_2_0_0, min=52, max=52)
    age_0_0_0_2_0_1 = NumericalQidHierarchyNode(parent=age_0_0_0_2_0, min=53, max=54)
    age_0_0_0_2_0_1_0 = NumericalQidHierarchyNode(parent=age_0_0_0_2_0_1, min=53, max=53)
    age_0_0_0_2_0_1_1 = NumericalQidHierarchyNode(parent=age_0_0_0_2_0_1, min=54, max=54)
    age_0_0_0_2_1 = NumericalQidHierarchyNode(parent=age_0_0_0_2, min=55, max=57)
    age_0_0_0_2_1_0 = NumericalQidHierarchyNode(parent=age_0_0_0_2_1, min=55, max=55)
    age_0_0_0_2_1_1 = NumericalQidHierarchyNode(parent=age_0_0_0_2_1, min=56, max=56)
    age_0_0_0_2_1_2 = NumericalQidHierarchyNode(parent=age_0_0_0_2_1, min=57, max=57)
    age_0_0_1 = NumericalQidHierarchyNode(parent=age_0_0, min=58, max=65)
    age_0_0_1_0 = NumericalQidHierarchyNode(parent=age_0_0_1, min=58, max=61)
    age_0_0_1_0_0 = NumericalQidHierarchyNode(parent=age_0_0_1_0, min=58, max=59)
    age_0_0_1_0_0_0 = NumericalQidHierarchyNode(parent=age_0_0_1_0_0, min=58, max=58)
    age_0_0_1_0_0_1 = NumericalQidHierarchyNode(parent=age_0_0_1_0_0, min=59, max=59)
    age_0_0_1_0_1 = NumericalQidHierarchyNode(parent=age_0_0_1_0, min=60, max=61)
    age_0_0_1_0_1_0 = NumericalQidHierarchyNode(parent=age_0_0_1_0_1, min=60, max=60)
    age_0_0_1_0_1_1 = NumericalQidHierarchyNode(parent=age_0_0_1_0_1, min=61, max=61)
    age_0_0_1_1 = NumericalQidHierarchyNode(parent=age_0_0_1, min=62, max=65)
    age_0_1 = NumericalQidHierarchyNode(parent=age_0, min=66, max=76)
    age_0_1_0 = NumericalQidHierarchyNode(parent=age_0_1, min=66, max=72)
    age_0_1_0_0 = NumericalQidHierarchyNode(parent=age_0_1_0, min=66, max=69)
    age_0_1_0_0_0 = NumericalQidHierarchyNode(parent=age_0_1_0_0, min=66, max=67)
    age_0_1_0_0_0_0 = NumericalQidHierarchyNode(parent=age_0_1_0_0_0, min=66, max=66)
    age_0_1_0_0_0_1 = NumericalQidHierarchyNode(parent=age_0_1_0_0_0, min=67, max=67)
    age_0_1_0_0_1 = NumericalQidHierarchyNode(parent=age_0_1_0_0, min=68, max=69)
    age_0_1_0_0_1_0 = NumericalQidHierarchyNode(parent=age_0_1_0_0_1, min=68, max=68)
    age_0_1_0_0_1_1 = NumericalQidHierarchyNode(parent=age_0_1_0_0_1, min=69, max=69)
    age_0_1_0_1 = NumericalQidHierarchyNode(parent=age_0_1_0, min=70, max=72)
    age_0_1_0_1_0 = NumericalQidHierarchyNode(parent=age_0_1_0_1, min=70, max=70)
    age_0_1_0_1_1 = NumericalQidHierarchyNode(parent=age_0_1_0_1, min=71, max=71)
    age_0_1_0_1_2 = NumericalQidHierarchyNode(parent=age_0_1_0_1, min=72, max=72)
    age_0_1_1 = NumericalQidHierarchyNode(parent=age_0_1, min=73, max=76)
    age_0_1_1_0 = NumericalQidHierarchyNode(parent=age_0_1_1, min=73, max=74)
    age_0_1_1_0_0 = NumericalQidHierarchyNode(parent=age_0_1_1_0, min=73, max=73)
    age_0_1_1_0_1 = NumericalQidHierarchyNode(parent=age_0_1_1_0, min=74, max=74)
    age_0_1_1_1 = NumericalQidHierarchyNode(parent=age_0_1_1, min=75, max=76)
    age_0_1_1_1_0 = NumericalQidHierarchyNode(parent=age_0_1_1_1, min=75, max=75)
    age_0_1_1_1_1 = NumericalQidHierarchyNode(parent=age_0_1_1_1, min=76, max=76)
    age_1 = NumericalQidHierarchyNode(parent=age_root, min=77, max=119)
    age_1_0 = NumericalQidHierarchyNode(parent=age_1, min=77, max=82)
    age_1_0_0 = NumericalQidHierarchyNode(parent=age_1_0, min=77, max=79)
    age_1_0_0_0 = NumericalQidHierarchyNode(parent=age_1_0_0, min=77, max=77)
    age_1_0_0_1 = NumericalQidHierarchyNode(parent=age_1_0_0, min=78, max=78)
    age_1_0_0_2 = NumericalQidHierarchyNode(parent=age_1_0_0, min=79, max=79)
    age_1_0_1 = NumericalQidHierarchyNode(parent=age_1_0, min=80, max=82)
    age_1_0_1_0 = NumericalQidHierarchyNode(parent=age_1_0_1, min=80, max=80)
    age_1_0_1_1 = NumericalQidHierarchyNode(parent=age_1_0_1, min=81, max=81)
    age_1_0_1_2 = NumericalQidHierarchyNode(parent=age_1_0_1, min=82, max=82)
    age_1_1 = NumericalQidHierarchyNode(parent=age_1, min=83, max=119)
    age_1_1_0 = NumericalQidHierarchyNode(parent=age_1_1, min=83, max=87)
    age_1_1_0_0 = NumericalQidHierarchyNode(parent=age_1_1_0, min=83, max=84)
    age_1_1_0_0_0 = NumericalQidHierarchyNode(parent=age_1_1_0_0, min=83, max=83)
    age_1_1_0_0_1 = NumericalQidHierarchyNode(parent=age_1_1_0_0, min=84, max=84)
    age_1_1_0_1 = NumericalQidHierarchyNode(parent=age_1_1_0, min=85, max=87)
    age_1_1_0_1_0 = NumericalQidHierarchyNode(parent=age_1_1_0_1, min=85, max=85)
    age_1_1_0_1_1 = NumericalQidHierarchyNode(parent=age_1_1_0_1, min=86, max=86)
    age_1_1_0_1_2 = NumericalQidHierarchyNode(parent=age_1_1_0_1, min=87, max=87)
    age_1_1_1 = NumericalQidHierarchyNode(parent=age_1_1, min=88, max=119)
    age_1_1_1_0 = NumericalQidHierarchyNode(parent=age_1_1_1, min=88, max=91)
    age_1_1_1_0_0 = NumericalQidHierarchyNode(parent=age_1_1_1_0, min=88, max=89)
    age_1_1_1_0_0_0 = NumericalQidHierarchyNode(parent=age_1_1_1_0_0, min=88, max=88)
    age_1_1_1_0_0_1 = NumericalQidHierarchyNode(parent=age_1_1_1_0_0, min=89, max=89)
    age_1_1_1_0_1 = NumericalQidHierarchyNode(parent=age_1_1_1_0, min=90, max=91)
    age_1_1_1_1 = NumericalQidHierarchyNode(parent=age_1_1_1, min=92, max=99)
    age_1_1_1_1_0 = NumericalQidHierarchyNode(parent=age_1_1_1_1, min=92, max=93)
    age_1_1_1_1_0_0 = NumericalQidHierarchyNode(parent=age_1_1_1_1_0, min=92, max=92)
    age_1_1_1_1_0_1 = NumericalQidHierarchyNode(parent=age_1_1_1_1_0, min=93, max=93)
    age_1_1_1_1_1 = NumericalQidHierarchyNode(parent=age_1_1_1_1, min=94, max=99)
    age_1_1_1_1_1_0 = NumericalQidHierarchyNode(parent=age_1_1_1_1_1, min=94, max=95)
    age_1_1_1_1_1_1 = NumericalQidHierarchyNode(parent=age_1_1_1_1_1, min=96, max=99)
    age_1_1_1_2 = NumericalQidHierarchyNode(parent=age_1_1_1, min=100, max=119)

    return age_root


ATTRIBUTES = ["Center", "Age", "Sex", "Pre-mRS", "NIHSS_AD", "Thrombozyten_Aggregationshemmung", "Antikoorgulation",
              "Hypertonus", "Dm", "VHF", "Smoking", "Occluded_vessel_ACI", "Occluded_vessel_MCA", "ASPECTS",
              "Additional_IVT", "Final_TICI_Score", "NIHSS_24h", "mRS_Discharge", "In-hospital_death", "mRS_90-days"]
SEX_INDEX = ATTRIBUTES.index("Sex")
AGE_INDEX = ATTRIBUTES.index("Age")

attribute_trees = {
    AGE_INDEX: get_age_tree(),
    SEX_INDEX: get_sex_tree()
}

# data

my_path = os.path.abspath(os.path.dirname(__file__))
DATA_FILE = 'data/sampled_data_rnd_ascending_center_nrs.csv'
DATA_PATH = os.path.join(os.path.dirname(my_path), DATA_FILE)