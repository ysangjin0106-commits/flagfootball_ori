# 플레이 시뮬레이션 로직
import random
from typing import List
from data.players import Player
from data.strategies import OffenseStrategy, DefenseStrategy


def _avg(players: List[Player], attr: str) -> float:
    return sum(getattr(p, attr) for p in players) / len(players)


def _pick(players: List[Player], *positions) -> Player:
    """포지션 우선순위로 선수 선택. 없으면 첫 번째 선수 반환."""
    for pos in positions:
        pool = [p for p in players if p.position == pos]
        if pool:
            return random.choice(pool)
    return players[0]


def simulate_play(
    offense_team: List[Player],
    defense_team: List[Player],
    off_strategy: OffenseStrategy,
    def_strategy: DefenseStrategy,
) -> dict:
    """
    한 플레이를 시뮬레이션. 반환값: {"yards", "result", "description", "qb", "receiver", "db"}
    """
    def_speed   = _avg(defense_team, "speed")
    def_defense = _avg(defense_team, "defense")
    def_agility = _avg(defense_team, "agility")

    qb  = _pick(offense_team, "QB")
    db  = _pick(defense_team, "DB")
    is_run = (off_strategy == "conservative")

    # 공격 스탯 계산 (런 vs 패스)
    if is_run:
        carrier  = _pick(offense_team, "RB", "WR")
        off_score = (carrier.speed * 0.5 + carrier.agility * 0.5) / 10
    else:
        receiver  = _pick(offense_team, "WR", "RB")
        off_score = (qb.throwing * 0.4 + _avg(offense_team, "catching") * 0.3 +
                     _avg(offense_team, "agility") * 0.3) / 10

    def_score = (def_defense * 0.4 + def_speed * 0.3 + def_agility * 0.3) / 10

    # 전략 보정
    strategy_bonus = {
        "aggressive":   {"base_yards": 10, "success_mod": -0.10, "big_play_chance": 0.25},
        "balanced":     {"base_yards":  6, "success_mod":  0.00, "big_play_chance": 0.10},
        "conservative": {"base_yards":  5, "success_mod":  0.10, "big_play_chance": 0.05},
    }[off_strategy]

    def_bonus = {
        "blitz": {"pressure": 0.20, "coverage": -0.15},
        "zone":  {"pressure": 0.00, "coverage":  0.10},
        "man":   {"pressure": 0.05, "coverage":  0.15},
    }[def_strategy]

    # 런 플레이는 블리츠에 강함
    if is_run and def_strategy == "blitz":
        def_bonus["pressure"] = -0.05

    base_success = 0.55 + off_score - def_score
    base_success += strategy_bonus["success_mod"]
    base_success -= def_bonus["pressure"]
    base_success -= def_bonus["coverage"] * 0.5
    base_success = max(0.15, min(0.85, base_success))

    roll = random.random()

    if roll < base_success:
        if random.random() < strategy_bonus["big_play_chance"]:
            yards = random.randint(15, 40)
            if is_run:
                actor  = carrier
                desc   = f"{carrier.name} 대런! {yards}야드 돌파"
            else:
                actor  = receiver
                desc   = f"{qb.name} → {receiver.name} 롱패스! {yards}야드"
            result = "big_play"
        else:
            yards = random.randint(3, strategy_bonus["base_yards"])
            if is_run:
                actor  = carrier
                desc   = f"{carrier.name} 러닝, {yards}야드 전진"
            else:
                actor  = receiver
                desc   = f"{qb.name} → {receiver.name}, {yards}야드 전진"
            result = "success"
    else:
        actor = qb
        if not is_run and def_bonus["pressure"] > 0.1 and random.random() < 0.4:
            # QB 압박 상황 — 새크 or 미완성
            if random.random() < 0.35:
                yards  = random.randint(-7, -2)
                desc   = f"QB 새크! {qb.name} {abs(yards)}야드 손실"
                result = "sack"
            else:
                yards  = 0
                desc   = f"QB 압박! {qb.name} 패스 미완성"
                result = "incomplete"
        else:
            yards  = 0
            target = carrier if is_run else receiver
            desc   = f"{db.name}, {target.name} 플래그 뽑기!"
            result = "failure"

    return {
        "yards":       yards,
        "result":      result,
        "description": desc,
        "is_run":      is_run,
    }
