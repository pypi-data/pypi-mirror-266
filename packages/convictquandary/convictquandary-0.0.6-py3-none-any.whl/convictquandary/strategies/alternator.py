from ..constants import Action, Belief, Persuasion
from ..strategy import Strategy


class Alternator(Strategy):

    meta = {"strategy_set": "axelrod1984"}

    def get_action(
        self,
        player_actions: list[Action],
        player_persuasions: list[Persuasion],
        player_beliefs: list[Belief],
        opponent_actions: list[Action],
        opponent_persuasions: list[Persuasion],
    ) -> Action:
        if not player_actions:
            return Action.COOPERATE
        return (
            Action.DEFECT
            if player_actions[-1] == Action.COOPERATE
            else Action.COOPERATE
        )
