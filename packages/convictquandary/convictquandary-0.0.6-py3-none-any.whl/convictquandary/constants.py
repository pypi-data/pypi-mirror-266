from enum import Enum


class Action(Enum):

    COOPERATE = 1
    DEFECT = 2
    DNF = 3  # Did not finish (Error in player output)


class Persuasion(Enum):

    TRUTH = 1
    LIE = 2
    DNF = 3  # Did not finish (Error in player output)


class Belief(Enum):

    BELIEVE = 1
    DOUBT = 2
    DNF = 3  # Did not finish (Error in player output)
