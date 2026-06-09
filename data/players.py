# 선수 데이터 정의
from dataclasses import dataclass
from typing import Literal

Position = Literal["QB", "WR", "RB", "DB"]

@dataclass
class Player:
    name: str
    position: Position
    speed: int       # 스피드 (1~10)
    catching: int    # 캐칭 (1~10)
    throwing: int    # 패스 정확도 (1~10, QB 전용)
    agility: int     # 민첩성 (1~10)
    defense: int     # 수비/플래그 뽑기 (1~10)

    def overall(self) -> int:
        return (self.speed + self.catching + self.throwing + self.agility + self.defense) // 5


# ── 플레이어 팀 풀 ─────────────────────────────────
# 0~4: 선발, 5~9: 교체
PLAYER_POOL = [
    # 선발
    Player("Kim Joon",  "QB", speed=6, catching=5, throwing=9, agility=7, defense=4),
    Player("Lee Seo",   "WR", speed=9, catching=8, throwing=2, agility=8, defense=4),
    Player("Park Min",  "WR", speed=7, catching=9, throwing=2, agility=6, defense=5),
    Player("Choi Hyun", "RB", speed=8, catching=6, throwing=2, agility=9, defense=5),
    Player("Jung Woo",  "DB", speed=7, catching=4, throwing=2, agility=7, defense=9),
    # 교체
    Player("Han Sol",   "WR", speed=8, catching=7, throwing=2, agility=7, defense=4),
    Player("Yoon Gi",   "DB", speed=6, catching=3, throwing=2, agility=6, defense=8),
    Player("Oh Jae",    "QB", speed=5, catching=4, throwing=7, agility=6, defense=3),
    Player("Shin Ho",   "RB", speed=9, catching=5, throwing=2, agility=8, defense=4),
    Player("Im Chan",   "WR", speed=7, catching=8, throwing=2, agility=8, defense=5),
]

# ── AI 상대팀 풀 ───────────────────────────────────
# 0~4: 선발, 5~9: 교체
AI_PLAYER_POOL = [
    # 선발
    Player("Rival QB",  "QB", speed=6, catching=5, throwing=8, agility=6, defense=4),
    Player("Fast WR",   "WR", speed=9, catching=7, throwing=2, agility=8, defense=3),
    Player("Sure WR",   "WR", speed=6, catching=9, throwing=2, agility=6, defense=4),
    Player("Power RB",  "RB", speed=7, catching=5, throwing=2, agility=8, defense=5),
    Player("Cover DB",  "DB", speed=7, catching=3, throwing=2, agility=7, defense=9),
    # 교체
    Player("Speedy WR", "WR", speed=10, catching=6, throwing=2, agility=9, defense=3),
    Player("Clutch QB", "QB", speed=5,  catching=4, throwing=9, agility=5, defense=3),
    Player("Tank RB",   "RB", speed=6,  catching=5, throwing=2, agility=7, defense=6),
    Player("Shadow DB", "DB", speed=8,  catching=3, throwing=2, agility=8, defense=8),
    Player("Flex WR",   "WR", speed=7,  catching=8, throwing=2, agility=7, defense=5),
]
