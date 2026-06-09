import pygame
from typing import Optional
from .base import BaseScene
from state import GameState
from controller import max_downs
from ui.renderer import draw_text, draw_title, draw_scoreboard
from ui.field_renderer import FieldRenderer
from data.strategies import OFFENSE_LABELS, DEFENSE_LABELS
from constants import (
    YELLOW, GRAY, GOLD, WHITE, SCREEN_W, SCREEN_H,
    FIELD_Y, FIELD_H, TOTAL_POSSESSIONS, DOWNS_BEFORE_MID,
)


class ResultScene(BaseScene):
    def __init__(self, gs: GameState, fonts: dict):
        self.gs = gs
        self.fonts = fonts
        self._field = FieldRenderer()

    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        if event.type != pygame.KEYDOWN or event.key != pygame.K_RETURN:
            return None

        gs = self.gs
        if gs.possession_count >= TOTAL_POSSESSIONS:
            return "gameover"

        # 미드필드 미돌파 상태에서 마지막 다운 직전 → 펀트 선택지 제공 (플레이어만)
        if gs.possession == "player" and not gs.crossed_midfield and gs.down == DOWNS_BEFORE_MID:
            return "punt"

        return "strategy"

    def draw(self, screen: pygame.Surface) -> None:
        gs = self.gs
        draw_title(screen, "플레이 결과", self.fonts["lg"])
        draw_scoreboard(screen, gs.player_score, gs.ai_score, self.fonts["md"])
        self._field.draw(screen, gs.ball_yard, gs.yards_to_go,
                         gs.possession, gs.crossed_midfield, self.fonts["sm"])

        base_y = FIELD_Y + FIELD_H + 12

        # 플레이 결과 메시지
        draw_text(screen, gs.message, SCREEN_W // 2, base_y, self.fonts["md"], YELLOW, center=True)

        # AI 전략 공개
        if gs.ai_last_offense or gs.ai_last_defense:
            ai_off_label = OFFENSE_LABELS.get(gs.ai_last_offense or "", gs.ai_last_offense or "")
            ai_def_label = DEFENSE_LABELS.get(gs.ai_last_defense or "", gs.ai_last_defense or "")
            info = f"상대  공격: {ai_off_label}  |  수비: {ai_def_label}"
            draw_text(screen, info, SCREEN_W // 2, base_y + 32, self.fonts["sm"], GOLD, center=True)

        # 다운 / 남은 야드 상황
        if gs.possession_count < TOTAL_POSSESSIONS:
            max_d    = max_downs(gs)
            phase    = "터치다운까지" if gs.crossed_midfield else "미드필드까지"
            status   = f"{gs.down}/{max_d}다운  |  {phase} {gs.yards_to_go}야드"
            draw_text(screen, status, SCREEN_W // 2, base_y + 62, self.fonts["sm"], GRAY, center=True)
            draw_text(screen, "Enter → 다음", SCREEN_W // 2, SCREEN_H - 20, self.fonts["sm"], GRAY, center=True)
