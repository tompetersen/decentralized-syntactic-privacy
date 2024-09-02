import os

from src.qid_hierarchy_node import CategoricalQidHierarchyNode, NumericalQidHierarchyNode


"""
ADULT data set
https://archive.ics.uci.edu/ml/datasets/adult

---
Contained data has the following fields:

>50K, <=50K.

age: continuous.
workclass: Private, Self-emp-not-inc, Self-emp-inc, Federal-gov, Local-gov, State-gov, Without-pay, Never-worked.
fnlwgt: continuous.
education: Bachelors, Some-college, 11th, HS-grad, Prof-school, Assoc-acdm, Assoc-voc, 9th, 7th-8th, 12th, Masters, 1st-4th, 10th, Doctorate, 5th-6th, Preschool.
education-num: continuous.
marital-status: Married-civ-spouse, Divorced, Never-married, Separated, Widowed, Married-spouse-absent, Married-AF-spouse.
occupation: Tech-support, Craft-repair, Other-service, Sales, Exec-managerial, Prof-specialty, Handlers-cleaners, Machine-op-inspct, Adm-clerical, Farming-fishing, Transport-moving, Priv-house-serv, Protective-serv, Armed-Forces.
relationship: Wife, Own-child, Husband, Not-in-family, Other-relative, Unmarried.
race: White, Asian-Pac-Islander, Amer-Indian-Eskimo, Other, Black.
sex: Female, Male.
capital-gain: continuous.
capital-loss: continuous.
hours-per-week: continuous.
native-country: United-States, Cambodia, England, Puerto-Rico, Canada, Germany, Outlying-US(Guam-USVI-etc), India, Japan, Greece, South, China, Cuba, Iran, Honduras, Philippines, Italy, Poland, Jamaica, Vietnam, Mexico, Portugal, Ireland, France, Dominican-Republic, Laos, Ecuador, Taiwan, Haiti, Columbia, Hungary, Guatemala, Nicaragua, Scotland, Thailand, Yugoslavia, El-Salvador, Trinadad&Tobago, Peru, Hong, Holand-Netherlands.
---

"""


# hierarchy trees

# sex

root_node = CategoricalQidHierarchyNode("ANY")
CategoricalQidHierarchyNode("Male", root_node)
CategoricalQidHierarchyNode("Female", root_node)
ADULT_SEX_TREE = root_node

# race

root_node = CategoricalQidHierarchyNode("ANY")
CategoricalQidHierarchyNode("White", root_node)
nw_node = CategoricalQidHierarchyNode("Non-White", root_node)
CategoricalQidHierarchyNode("Asian-Pac-Islander", nw_node)
CategoricalQidHierarchyNode("Amer-Indian-Eskimo", nw_node)
CategoricalQidHierarchyNode("Other", nw_node)
CategoricalQidHierarchyNode("Black", nw_node)
ADULT_RACE_TREE = root_node


# age

MIN_AGE = 0
MAX_AGE = 100
ADULT_AGE_TREE = NumericalQidHierarchyNode.create_balanced_numerical_hierarchy(MIN_AGE, MAX_AGE)


"""
occupation

Own categorization for testing purposes:
    Other-service,
    technical,
        Tech-support,
        Craft-repair,
        Machine-op-inspct,
    office,
        Sales,
        Exec-managerial,
        Prof-specialty,
        Adm-clerical,
    logistics,
        Farming-fishing,
        Transport-moving,
        Priv-house-serv,
        Handlers-cleaners,
    protection
        Protective-serv,
        Armed-Forces
"""
root_node = CategoricalQidHierarchyNode("ANY")
CategoricalQidHierarchyNode("Other-service", root_node)
technical = CategoricalQidHierarchyNode("technical", root_node)
office = CategoricalQidHierarchyNode("office", root_node)
logistics = CategoricalQidHierarchyNode("logistics", root_node)
protection = CategoricalQidHierarchyNode("protection", root_node)
CategoricalQidHierarchyNode("Tech-support", technical)
CategoricalQidHierarchyNode("Craft-repair", technical)
CategoricalQidHierarchyNode("Machine-op-inspct", technical)
CategoricalQidHierarchyNode("Sales", office)
CategoricalQidHierarchyNode("Exec-managerial", office)
CategoricalQidHierarchyNode("Prof-specialty", office)
CategoricalQidHierarchyNode("Adm-clerical", office)
CategoricalQidHierarchyNode("Farming-fishing", logistics)
CategoricalQidHierarchyNode("Transport-moving", logistics)
CategoricalQidHierarchyNode("Priv-house-serv", logistics)
CategoricalQidHierarchyNode("Handlers-cleaners", logistics)
CategoricalQidHierarchyNode("Protective-serv", protection)
CategoricalQidHierarchyNode("Armed-Forces", protection)
OCCUPATION_TREE = root_node


# education-num

EDU_NUM_MIN = 0
EDU_NUM_MAX = 16
EDUCATION_NUM_TREE = NumericalQidHierarchyNode.create_balanced_numerical_hierarchy(EDU_NUM_MIN, EDU_NUM_MAX)

"""
marital status

Own categorization for testing purposes:

Never-married
Married
    Married-civ-spouse // Married-civ-spouse corresponds to a civilian spouse 
    Married-AF-spouse // while Married-AF-spouse is a spouse in the Armed Forces.
Other 
    Separated
    Divorced
    Widowed
    Married-spouse-absent
"""

root_node = CategoricalQidHierarchyNode("ANY")
CategoricalQidHierarchyNode("Never-married", root_node)
married = CategoricalQidHierarchyNode("Married", root_node)
other = CategoricalQidHierarchyNode("Other", root_node)
CategoricalQidHierarchyNode("Married-civ-spouse", married)
CategoricalQidHierarchyNode("Married-AF-spouse", married)
CategoricalQidHierarchyNode("Separated", other)
CategoricalQidHierarchyNode("Divorced", other)
CategoricalQidHierarchyNode("Widowed", other)
CategoricalQidHierarchyNode("Married-spouse-absent", other)
MARITAL_STATUS_TREE = root_node

attribute_trees = {
    0: ADULT_AGE_TREE,
    4: EDUCATION_NUM_TREE,
    5: MARITAL_STATUS_TREE,
    6: OCCUPATION_TREE,
    8: ADULT_RACE_TREE,
    9: ADULT_SEX_TREE,
}


# data


my_path = os.path.abspath(os.path.dirname(__file__))
DATA_FILE = 'data/adult_complete.csv'
DATA_PATH = os.path.join(os.path.dirname(my_path), DATA_FILE)
