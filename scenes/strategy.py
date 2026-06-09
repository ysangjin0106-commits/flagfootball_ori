import pygame
from typing import Optional
from .base import BaseScene
from state import GameState
from controller import execute_play, is_no_run_zone, max_downs
from ui.renderer import draw_text, draw_title, draw_scoreboard, draw_field
from data.strategies import OFFENSE_LABELS, DEFENSE_LABELS
from constants import GOLD, YELLOW, GRAY, RED, WHITE, SCREEN_W, SCREEN_H, FIELD_Y, FIELD_H

_ORANGE = (255, 140, 0)


class StrategyScene(BaseScene):
    def __init__(self, gs: GameState, fonts: dict):
        self.gs = gs
        self.fonts = fonts

    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        if event.type != pygame.KEYDOWN:
            return None
        key = event.key
        off_keys = [pygame.K_1, pygame.K_2, pygame.K_3]
        def_keys  = [pygame.K_4, pygame.K_5, pygame.K_6]

        if key in off_keys:
            idx = off_keys.index(key)
            # NRZ에서 런플레이([1] conservative) 선택 차단
            if idx == 2 and is_no_run_zone(self.gs):
                pass
            else:
                self.gs.off_idx = idx

        if key in def_keys:
            self.gs.def_idx = def_keys.index(key)

        if key == pygame.K_RETURN:
            execute_play(self.gs)
            return "animation"
        return None

    def draw(self, screen: pygame.Surface) -> None:
        gs = self.gs
        max_d   = max_downs(gs)
        phase   = "터치다운까지" if gs.crossed_midfield else "미드필드까지"
        possession_str = "우리 팀 공격" if gs.possession == "player" else "AI 팀 공격 (수비 중)"

        draw_title(screen, f"{possession_str}  |  {gs.down}/{max_d}다운  {phase} {gs.yards_to_go}야드",
                   self.fonts["lg"])
        draw_scoreboard(screen, gs.player_score, gs.ai_score, self.fonts["md"])
        draw_field(screen, gs.ball_yard, gs.yards_to_go,
                   gs.possession, gs.crossed_midfield, self.fonts["sm"])

        panel_y  = FIELD_Y + FIELD_H + 20
        off_opts = list(OFFENSE_LABELS.items())
        def_opts = list(DEFENSE_LABELS.items())
        in_nrz   = is_no_run_zone(gs)

        if gs.possession == "player":
            draw_text(screen, "공격 전략  [1] [2] [3]", 80, panel_y, self.fonts["md"], GOLD)
            for i, (key, label) in enumerate(off_opts):
                is_run_opt = (key == "conservative")
                if is_run_opt and in_nrz:
                    # 런 금지구역: 회색 + 취소선 텍스트
                    draw_text(screen, f"[{i+1}] {label}  ← 런 금지구역", 80,
                              panel_y + 32 + i * 28, self.fonts["sm"], GRAY)
                else:
                    color = YELLOW if i == gs.off_idx else GRAY
                    draw_text(screen, f"[{i+1}] {label}", 80,
                              panel_y + 32 + i * 28, self.fonts["sm"], color)

            # NRZ 경고 배너
            if in_nrz:
                draw_text(screen, "[ No Run Zone — 패스 플레이만 가능 ]",
                          80, panel_y + 32 + len(off_opts) * 28 + 6,
                          self.fonts["sm"], _ORANGE)

        draw_text(screen, "수비 전략  [4] [5] [6]", 520, panel_y, self.fonts["md"], GOLD)
        for i, (_, v) in enumerate(def_opts):
            color = YELLOW if i == gs.def_idx else GRAY
            draw_text(screen, f"[{i+4}] {v}", 520, panel_y + 32 + i * 28, self.fonts["sm"], color)

        draw_text(screen, "Enter → 플레이 실행", SCREEN_W // 2, SCREEN_H - 20,
                  self.fonts["sm"], GRAY, center=True)
