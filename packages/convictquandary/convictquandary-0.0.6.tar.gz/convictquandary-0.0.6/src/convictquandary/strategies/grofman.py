from random import choices

from ..constants import Action, Belief, Persuasion
from ..strategy import Strategy


class Grofman(Strategy):

    meta = {"strategy_set": "axelrod1984"}

    def get_action(
        self,
        player_actions: list[Action],
        player_persuasions: list[Persuasion],
        player_beliefs: list[Belief],
        opponent_actions: list[Action],
        opponent_persuasions: list[Persuasion],
    ) -> Action:
        if len(player_actions) == 0 or player_actions[-1] == opponent_actions[-1]:
            return Action.COOPERATE
        return choices(
            [Action.COOPERATE, Action.DEFECT], weights=[2 / 7, 1 - 2 / 7]
        )[  # nosec
            0  # nosec
        ]  # nosec
