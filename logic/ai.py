# AI 상대 전략 결정 로직
import random
from data.strategies import OffenseStrategy, DefenseStrategy


def ai_choose_offense(down: int, yards_to_go: int, score_diff: int) -> OffenseStrategy:
    """상황에 따라 AI 공격 전략 선택"""
    if score_diff < -7:
        # 지고 있으면 공격적으로
        return random.choices(["aggressive", "balanced", "conservative"], weights=[60, 30, 10])[0]
    elif yards_to_go >= 10:
        return random.choices(["aggressive", "balanced", "conservative"], weights=[40, 40, 20])[0]
    elif down == 4:
        # 4번째 다운은 과감하게
        return random.choices(["aggressive", "balanced", "conservative"], weights=[50, 35, 15])[0]
    else:
        return random.choices(["aggressive", "balanced", "conservative"], weights=[25, 45, 30])[0]


def ai_choose_defense(down: int, yards_to_go: int, score_diff: int) -> DefenseStrategy:
    """상황에 따라 AI 수비 전략 선택"""
    if score_diff > 7:
        # 이기고 있으면 안전하게 존 수비
        return random.choices(["blitz", "zone", "man"], weights=[15, 55, 30])[0]
    elif yards_to_go <= 3:
        # 단거리는 맨투맨으로 막기
        return random.choices(["blitz", "zone", "man"], weights=[20, 30, 50])[0]
    else:
        return random.choices(["blitz", "zone", "man"], weights=[30, 40, 30])[0]
