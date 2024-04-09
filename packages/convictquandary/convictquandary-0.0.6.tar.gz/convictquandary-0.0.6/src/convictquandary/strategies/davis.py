from ..constants import Action, Belief, Persuasion
from ..strategy import Strategy


class Davis(Strategy):

    meta = {"strategy_set": "axelrod1984"}

    def get_action(
        self,
        player_actions: list[Action],
        player_persuasions: list[Persuasion],
        player_beliefs: list[Belief],
        opponent_actions: list[Action],
        opponent_persuasions: list[Persuasion],
    ) -> Action:
        if len(player_actions) < 10:
            return Action.COOPERATE
        if Action.DEFECT in opponent_actions:
            return Action.DEFECT
        return Action.COOPERATE
