import warnings

from .constants import Action, Persuasion
from .player import Player
from .strategy import Strategy
from .utils import exception_factory


class Game:

    def __init__(self, player1: Strategy, player2: Strategy, ngames: int = 1) -> None:
        self.player1 = Player(player1)
        self.player2 = Player(player2)
        self.score_matrix = {
            (Action.COOPERATE, Action.COOPERATE): (3, 3),
            (Action.COOPERATE, Action.DEFECT): (0, 5),
            (Action.DEFECT, Action.COOPERATE): (5, 0),
            (Action.DEFECT, Action.DEFECT): (0, 0),
            (Action.DNF, Action.COOPERATE): (0, 5),
            (Action.DNF, Action.DEFECT): (0, 5),
            (Action.COOPERATE, Action.DNF): (5, 0),
            (Action.DEFECT, Action.DNF): (5, 0),
            (Action.DNF, Action.DNF): (0, 0),
        }
        self.ngames = ngames
        self.game_scores = (0, 0)
        self.complete = False

    def play_game(self) -> None:
        if not self.complete:
            for i in range(0, self.ngames):
                player1_persuasion = self.player1.get_persuasion()
                player2_persuasion = self.player2.get_persuasion()
                player1_action = (
                    self.player1.play_move(player2_persuasion)
                    if player1_persuasion != Persuasion.DNF
                    else Action.DNF
                )
                player2_action = (
                    self.player2.play_move(player1_persuasion)
                    if player2_persuasion != Persuasion.DNF
                    else Action.DNF
                )
                current_game_score = self.score_matrix.get(
                    (player1_action, player2_action)
                )
                self.game_scores = tuple(
                    sum(x) for x in zip(self.game_scores, current_game_score)
                )
                self.player1.save_outcome(player2_action, current_game_score[0])
                self.player2.save_outcome(player1_action, current_game_score[1])
            self.complete = True
        else:
            raise exception_factory(ValueError, "Game already finished")

    def get_players(self) -> tuple[Strategy, Strategy]:
        return (self.player1.strategy, self.player2.strategy)

    def get_game_result(self) -> tuple[int, int]:
        if not self.complete:
            warnings.warn("Game has not been played yet")
        return self.game_scores
