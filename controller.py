from state import GameState
from logic.simulation import simulate_play
from logic.ai import ai_choose_offense, ai_choose_defense
from constants import (
    TD_YARDS, TOTAL_POSSESSIONS,
    MIDFIELD, NO_RUN_ZONE_WIDTH,
    PLAYER_START_YARD, AI_START_YARD,
    DOWNS_BEFORE_MID, DOWNS_AFTER_MID,
)

_OFF_LIST = ["aggressive", "balanced", "conservative"]
_DEF_LIST = ["blitz", "zone", "man"]


# ──────────────────────────────────────────────
# 헬퍼
# ──────────────────────────────────────────────

def is_no_run_zone(gs: GameState) -> bool:
    """현재 공격팀이 No Run Zone(런 금지구역)에 있는지 반환."""
    y = gs.ball_yard
    if gs.possession == "player":
        # 미드필드 직전 5야드(45~49) 또는 엔드존 직전 5야드(95~99)
        before_mid = (MIDFIELD - NO_RUN_ZONE_WIDTH) <= y < MIDFIELD
        before_end = (TD_YARDS  - NO_RUN_ZONE_WIDTH) <= y < TD_YARDS
        return before_mid or before_end
    else:
        # AI는 100→0 방향
        before_mid = MIDFIELD < y <= (MIDFIELD + NO_RUN_ZONE_WIDTH)
        before_end = 0        < y <= NO_RUN_ZONE_WIDTH
        return before_mid or before_end


def max_downs(gs: GameState) -> int:
    """현재 구간 최대 다운 수."""
    return DOWNS_AFTER_MID if gs.crossed_midfield else DOWNS_BEFORE_MID


def _update_yards_to_go(gs: GameState) -> None:
    """ball_yard 기준으로 다음 마일스톤까지 남은 야드를 갱신."""
    if gs.possession == "player":
        milestone = TD_YARDS if gs.crossed_midfield else MIDFIELD
        gs.yards_to_go = max(0, milestone - gs.ball_yard)
    else:
        milestone = 0 if gs.crossed_midfield else MIDFIELD
        gs.yards_to_go = max(0, gs.ball_yard - milestone)


# ──────────────────────────────────────────────
# 핵심 함수
# ──────────────────────────────────────────────

def execute_play(gs: GameState) -> None:
    """전략 확정 후 시뮬레이션 실행, 애니메이션 준비."""
    gs.selected_offense = _OFF_LIST[gs.off_idx]
    gs.selected_defense = _DEF_LIST[gs.def_idx]

    # No Run Zone: 런플레이 강제 취소
    if is_no_run_zone(gs) and gs.selected_offense == "conservative":
        gs.selected_offense = "balanced"

    score_diff = gs.player_score - gs.ai_score
    ai_off = ai_choose_offense(gs.down, gs.yards_to_go, -score_diff)
    ai_def = ai_choose_defense(gs.down, gs.yards_to_go, score_diff)

    gs.ai_last_offense = ai_off
    gs.ai_last_defense = ai_def

    if gs.possession == "player":
        result = simulate_play(gs.player_team, gs.ai_team, gs.selected_offense, ai_def)
    else:
        # AI 공격 중에도 NRZ 적용
        if is_no_run_zone(gs) and ai_off == "conservative":
            ai_off = "balanced"
        result = simulate_play(gs.ai_team, gs.player_team, ai_off, gs.selected_defense)

    gs.anim_result = result
    gs.anim_frame  = 0


def apply_play_result(gs: GameState) -> str:
    """애니메이션 결과를 상태에 반영. 다음 씬 이름을 반환."""
    yards = gs.anim_result["yards"]

    if gs.possession == "player":
        gs.ball_yard += yards
    else:
        gs.ball_yard -= yards

    # ── 세이프티 판정 (공격팀이 자기 엔드존으로 밀림) ──
    if gs.possession == "player" and gs.ball_yard <= 0:
        gs.ball_yard = PLAYER_START_YARD
        gs.ai_score += 2
        gs.message = "세이프티! 상대 2점 획득 — 공격권 교체"
        gs.crossed_midfield = False
        return end_drive(gs)

    if gs.possession == "ai" and gs.ball_yard >= TD_YARDS:
        gs.ball_yard = AI_START_YARD
        gs.player_score += 2
        gs.message = "세이프티! 우리 팀 2점 획득 — 공격권 교체"
        gs.crossed_midfield = False
        return end_drive(gs)

    # ── 터치다운 판정 ──
    if gs.possession == "player" and gs.ball_yard >= TD_YARDS:
        gs.player_score += 6
        gs.message = "터치다운! 6점 획득"
        gs.pat_pending = True
        return "pat"

    if gs.possession == "ai" and gs.ball_yard <= 0:
        gs.ai_score += 6
        gs.message = "AI 터치다운! 상대 6점"
        gs.pat_pending = True
        return "pat"

    # ── 미드필드 돌파 판정 ──
    if not gs.crossed_midfield:
        crossed = (
            (gs.possession == "player" and gs.ball_yard >= MIDFIELD) or
            (gs.possession == "ai"     and gs.ball_yard <= MIDFIELD)
        )
        if crossed:
            gs.crossed_midfield = True
            gs.down = 1
            _update_yards_to_go(gs)
            gs.message = f"미드필드 돌파! {DOWNS_AFTER_MID}다운 안에 터치다운을 노려라!"
            gs.last_play = gs.anim_result
            return "result"

    # ── 야드 갱신 후 다운 진행 ──
    _update_yards_to_go(gs)
    gs.down += 1
    gs.message = gs.anim_result["description"]

    if gs.down > max_downs(gs):
        gs.message += " — 공격권 교체"
        # 4th down go-for-it 실패 → 현 지점에서 공격권 교체
        if gs.went_for_it:
            gs.went_for_it = False
            return _end_drive_at_spot(gs)
        return end_drive(gs)

    gs.last_play = gs.anim_result
    return "result"


def end_drive(gs: GameState) -> str:
    """드라이브 종료. 상대팀이 5야드선(자기 진영)에서 시작."""
    gs.possession_count += 1
    if gs.possession_count >= TOTAL_POSSESSIONS:
        return "gameover"

    gs.possession        = "ai" if gs.possession == "player" else "player"
    gs.down              = 1
    gs.crossed_midfield  = False
    gs.went_for_it       = False
    gs.last_play         = None

    if gs.possession == "player":
        gs.ball_yard   = PLAYER_START_YARD
        gs.yards_to_go = MIDFIELD - PLAYER_START_YARD
    else:
        gs.ball_yard   = AI_START_YARD
        gs.yards_to_go = AI_START_YARD - MIDFIELD

    return "result"


def _end_drive_at_spot(gs: GameState) -> str:
    """4th down go-for-it 실패 시 현 지점에서 공격권 교체."""
    gs.possession_count += 1
    if gs.possession_count >= TOTAL_POSSESSIONS:
        return "gameover"

    gs.possession   = "ai" if gs.possession == "player" else "player"
    gs.down         = 1
    gs.last_play    = None

    # 현 볼 위치 기준으로 새 공격팀의 미드필드 통과 여부 결정
    if gs.possession == "player":
        gs.crossed_midfield = gs.ball_yard >= MIDFIELD
    else:
        gs.crossed_midfield = gs.ball_yard <= MIDFIELD

    _update_yards_to_go(gs)
    return "result"
