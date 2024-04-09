from random import choices

from ..constants import Action, Belief, Persuasion
from ..strategy import Strategy


class Tullock(Strategy):

    meta = {"strategy_set": "axelrod1984"}
    rounds_to_coop = 11

    def get_action(
        self,
        player_actions: list[Action],
        player_persuasions: list[Persuasion],
        player_beliefs: list[Belief],
        opponent_actions: list[Action],
        opponent_persuasions: list[Persuasion],
    ) -> Action:
        if len(player_actions) < self.rounds_to_coop:
            return Action.COOPERATE
        rounds = self.rounds_to_coop - 1
        cooperate_count = opponent_actions[-rounds:].count(Action.COOPERATE)
        prop_cooperate = cooperate_count / rounds
        prob_cooperate = max(0, prop_cooperate - 0.10)
        return choices(  # nosec
            [Action.COOPERATE, Action.DEFECT],  # nosec
            weights=[prob_cooperate, 1 - prob_cooperate],  # nosec
        )[  # nosec
            0  # nosec
        ]  # nosec
