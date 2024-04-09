from ..constants import Action, Belief, Persuasion
from ..strategy import Strategy


class TitForTat(Strategy):

    meta = {"strategy_set": "axelrod1984"}

    def get_action(
        self,
        player_actions: list[Action],
        player_persuasions: list[Persuasion],
        player_beliefs: list[Belief],
        opponent_actions: list[Action],
        opponent_persuasions: list[Persuasion],
    ) -> Action:
        if opponent_actions and opponent_actions[-1] == Action.DEFECT:
            return Action.DEFECT
        return Action.COOPERATE
