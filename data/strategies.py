# 전략 정의
from dataclasses import dataclass
from typing import Literal

OffenseStrategy = Literal["aggressive", "balanced", "conservative"]
DefenseStrategy = Literal["blitz", "zone", "man"]

@dataclass
class Strategy:
    offense: OffenseStrategy
    defense: DefenseStrategy


OFFENSE_LABELS = {
    "aggressive":   "딥패스 (롱패스·고위험)",
    "balanced":     "숏패스 (퀵 릴리즈)",
    "conservative": "런플레이 (RB 돌파)",
}

DEFENSE_LABELS = {
    "blitz": "블리츠 (QB 압박)",
    "zone":  "존 (구역 방어)",
    "man":   "맨투맨 (마크)",
}
