import pytest

from convictquandary import Action, Belief, Persuasion, Player, Strategy
from convictquandary.utils import exception_factory


def test_player_error_abstract_function_undefined():

    class StrategyWithError(Strategy):

        def get_persuasion(
            self,
            player_actions: list[Action],
            player_persuasions: list[Persuasion],
            player_beliefs: list[Belief],
            opponent_actions: list[Action],
            opponent_persuasions: list[Persuasion],
        ) -> Persuasion:
            return Persuasion.TRUTH  # pragma: no cover

    with pytest.raises(TypeError) as excinfo:
        Player(StrategyWithError)
    assert "Can't instantiate abstract class StrategyWithError" in str(excinfo.value)


def test_strategy_meta_type():

    with pytest.raises(TypeError, match="Strategy meta must be of type dict"):

        class StrategyWithMeta(Strategy):

            meta = 5

            def get_action(
                self,
                player_actions: list[Action],
                player_persuasions: list[Persuasion],
                player_beliefs: list[Belief],
                opponent_actions: list[Action],
                opponent_persuasions: list[Persuasion],
            ) -> Action:
                return Action.COOPERATE  # pragma: no cover

        Player(StrategyWithMeta)


def test_player_return_dnf_on_failure():

    class StrategyWithError(Strategy):

        def get_action(
            self,
            player_actions: list[Action],
            player_persuasions: list[Persuasion],
            player_beliefs: list[Belief],
            opponent_actions: list[Action],
            opponent_persuasions: list[Persuasion],
        ) -> Action:
            raise exception_factory(TypeError, "Random type error")

    player = Player(StrategyWithError)
    player_action = player.play_move(Persuasion.TRUTH)
    assert player_action == Action.DNF
