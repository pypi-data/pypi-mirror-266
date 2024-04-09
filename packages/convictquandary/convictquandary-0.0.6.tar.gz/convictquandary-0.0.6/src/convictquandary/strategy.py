from abc import ABC, abstractmethod

from .constants import Action, Belief, Persuasion
from .utils import exception_factory


class Strategy(ABC):

    @property
    def meta():
        pass

    def __init_subclass__(cls, **kwargs) -> None:
        if (cls.meta != Strategy.meta) and (not isinstance(cls.meta, dict)):
            raise exception_factory(TypeError, "Strategy meta must be of type dict")
        return super().__init_subclass__(**kwargs)

    def get_persuasion(
        self,
        player_actions: list[Action],
        player_persuasions: list[Persuasion],
        player_beliefs: list[Belief],
        opponent_actions: list[Action],
        opponent_persuasions: list[Persuasion],
    ) -> Persuasion:
        return Persuasion.TRUTH  # pragma: no cover

    def get_belief(
        self,
        player_actions: list[Action],
        player_persuasions: list[Persuasion],
        player_beliefs: list[Belief],
        opponent_actions: list[Action],
        opponent_persuasions: list[Persuasion],
    ) -> Belief:
        return Belief.BELIEVE  # pragma: no cover

    @abstractmethod
    def get_action(
        self,
        player_actions: list[Action],
        player_persuasions: list[Persuasion],
        player_beliefs: list[Belief],
        opponent_actions: list[Action],
        opponent_persuasions: list[Persuasion],
    ) -> Action:
        pass  # pragma: no cover
