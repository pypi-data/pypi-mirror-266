import random
import warnings
from itertools import combinations_with_replacement
from statistics import mean
from typing import Callable

from .game import Game
from .player import Player
from .strategy import Strategy
from .utils import exception_factory


class Tournament:

    def __init__(self, players: list[Strategy], ngames=1, seed=42) -> None:
        self.ngames = ngames
        self.players = players
        self.matches = {
            (p1.__name__, p2.__name__): Game(p1, p2, ngames=self.ngames)
            for p1, p2 in combinations_with_replacement(self.players, 2)
        }
        self.match_scores = None
        self.player_match_table = None
        self.complete = False
        random.seed(seed)

    def play_tournament(self) -> None:
        if not self.complete:
            [game.play_game() for game in self.matches.values()]
            self.match_scores = {
                tuple(
                    p.__class__.__name__ for p in game.get_players()
                ): game.get_game_result()
                for game in self.matches.values()
            }
            self.player_match_table = {
                player.__name__: {
                    k: v for k, v in self.match_scores.items() if player.__name__ in k
                }
                for player in self.players
            }
            self.complete = True
        else:
            raise exception_factory(ValueError, "Tournament already finished")

    def get_match_scores(self) -> dict[tuple[Player, Player], tuple[int, int]]:
        if not self.complete:
            warnings.warn("Tournament has not been played yet")
        return self.match_scores

    def get_player_scores(
        self, agg_func: Callable[[list[int]], float] = mean
    ) -> dict[Player, float]:
        if not self.complete:
            warnings.warn("Tournament has not been played yet")
        return {
            player: agg_func(self._unwrap_score_dict(matches, player))
            for player, matches in self.player_match_table.items()
        }

    def _unwrap_score_dict(self, scores: dict, player: str) -> list:
        return [v[k.index(player)] for k, v in scores.items()]
