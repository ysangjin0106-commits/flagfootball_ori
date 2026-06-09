from dataclasses import dataclass
from typing import List, Optional

from data.players import Player, PLAYER_POOL, AI_PLAYER_POOL
from data.strategies import OffenseStrategy, DefenseStrategy
from constants import MIDFIELD, PLAYER_START_YARD


@dataclass
class GameState:
    player_team:      List[Player]
    ai_team:          List[Player]
    player_bench:     List[Player]
    ai_bench:         List[Player]
    player_score:     int = 0
    ai_score:         int = 0
    possession:       str = "player"   # "player" | "ai"
    possession_count: int = 0
    down:             int = 1
    yards_to_go:      int = MIDFIELD - PLAYER_START_YARD   # 45 (미드필드까지)
    ball_yard:        int = PLAYER_START_YARD               # 5야드선 시작
    crossed_midfield: bool = False                          # 미드필드 돌파 여부
    went_for_it:      bool = False                          # 4th down go-for-it 선택 여부
    last_play:        Optional[dict] = None
    selected_offense: OffenseStrategy = "balanced"
    selected_defense: DefenseStrategy = "zone"
    anim_frame:       int = 0
    anim_result:      Optional[dict] = None
    off_idx:          int = 1
    def_idx:          int = 1
    message:          str = ""
    ai_last_offense:  Optional[str] = None
    ai_last_defense:  Optional[str] = None
    pat_pending:      bool = False


def new_state() -> GameState:
    return GameState(
        player_team  = list(PLAYER_POOL[:5]),
        ai_team      = list(AI_PLAYER_POOL[:5]),
        player_bench = list(PLAYER_POOL[5:]),
        ai_bench     = list(AI_PLAYER_POOL[5:]),
    )
