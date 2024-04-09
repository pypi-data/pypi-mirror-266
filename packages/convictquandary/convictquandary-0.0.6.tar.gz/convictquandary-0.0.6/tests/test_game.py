import pytest

from convictquandary import Action, Belief, Game, Persuasion, Strategy, utils
from convictquandary.strategies import Cooperator, Defector
from convictquandary.utils import exception_factory


def test_1v1_game_always_defect_win():
    game = Game(Cooperator, Defector, 200)
    game.play_game()
    assert game.get_game_result() == (
        0,
        1000,
    ), "Always defect not winning against always cooperate"


def test_1v1_game_always_defect_against_itself():
    game = Game(Defector, Defector, 200)
    game.play_game()
    assert game.get_game_result() == (0, 0), "Always defect against itself not 0"


def test_1v1_game_always_cooperate_against_itself():
    game = Game(Cooperator, Cooperator, 200)
    game.play_game()
    assert game.get_game_result() == (600, 600), "Always cooperate not score 600"


def test_1v1_game_get_players():
    player1 = Cooperator
    player2 = Cooperator
    game = Game(player1, player2, 200)
    p1, p2 = game.get_players()
    assert (type(p1), type(p2)) == (player1, player2), "Game returns correct players"


def test_1v1_game_already_played():
    game = Game(Cooperator, Cooperator, 200)
    game.play_game()
    with pytest.raises(ValueError, match="Game already finished"):
        game.play_game()


def test_utils_exception_factory():
    with pytest.raises(ValueError, match="Test message"):
        raise utils.exception_factory(ValueError, "Test message")


def test_player_error_in_action_in_game():

    class LogicWithError(Strategy):

        def get_action(
            self,
            player_actions: list[Action],
            player_persuasions: list[Persuasion],
            player_beliefs: list[Belief],
            opponent_actions: list[Action],
            opponent_persuasions: list[Persuasion],
        ) -> Action:
            raise exception_factory(NotImplementedError, "Player action error")

    game = Game(Cooperator, LogicWithError, 200)
    game.play_game()
    assert game.get_game_result() == (1000, 0), "Player with error not having 0 score"


def test_player_error_in_persuasion_in_game():

    class LogicWithError(Strategy):

        def get_persuasion(
            self,
            player_actions: list[Action],
            player_persuasions: list[Persuasion],
            player_beliefs: list[Belief],
            opponent_actions: list[Action],
            opponent_persuasions: list[Persuasion],
        ) -> Persuasion:
            raise exception_factory(NotImplementedError, "Player persuasion Error")

        def get_action(
            self,
            player_actions: list[Action],
            player_persuasions: list[Persuasion],
            player_beliefs: list[Belief],
            opponent_actions: list[Action],
            opponent_persuasions: list[Persuasion],
        ) -> Action:
            return Action.COOPERATE  # pragma: no cover

    game = Game(Cooperator, LogicWithError, 200)
    game.play_game()
    assert game.get_game_result() == (1000, 0), "Player with error not having 0 score"
