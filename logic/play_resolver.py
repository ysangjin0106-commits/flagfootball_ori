import random as _random_module
from typing import Any, List

from data.players import Player
from data.strategies import OffenseStrategy, DefenseStrategy
from logic.simulation import simulate_play


class PlayResolver:
    """
    simulate_play 를 rng 를 주입한 채로 래핑.
    테스트 코드에서 Random(seed=N) 을 넘기면 결과가 결정적.
    """

    def __init__(self, rng: Any = None):
        self.rng = rng or _random_module

    def resolve(
        self,
        offense_team: List[Player],
        defense_team: List[Player],
        off_strategy: OffenseStrategy,
        def_strategy: DefenseStrategy,
    ) -> dict:
        return simulate_play(
            offense_team, defense_team,
            off_strategy, def_strategy,
            rng=self.rng,
        )
