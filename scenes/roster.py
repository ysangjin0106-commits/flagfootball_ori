import pygame
from typing import Optional
from .base import BaseScene
from state import GameState
from ui.renderer import draw_text, draw_title
from constants import WHITE, YELLOW, GOLD, GRAY, RED, BLUE, SCREEN_W, SCREEN_H


def _grade(val: int) -> str:
    if val >= 8: return "S"
    if val >= 7: return "A"
    if val >= 6: return "B"
    if val >= 5: return "C"
    return "D"


class RosterScene(BaseScene):
    def __init__(self, gs: GameState, fonts: dict):
        self.gs = gs
        self.fonts = fonts
        self._btn = pygame.Rect(SCREEN_W // 2 - 100, SCREEN_H - 60, 200, 46)

    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        if event.type == pygame.MOUSEBUTTONDOWN and self._btn.collidepoint(event.pos):
            return "strategy"
        return None

    def _draw_team(self, screen, players, y_start: int, color, show_stats: bool):
        xs = [60, 200, 310, 380, 450, 520, 590, 660]
        headers = ["이름", "포지션", "SPD", "CAT", "THR", "AGI", "DEF", "OVR"]
        for i, h in enumerate(headers):
            draw_text(screen, h, xs[i], y_start, self.fonts["sm"], GOLD)
        y = y_start + 26
        for p in players:
            if show_stats:
                vals = [p.name, p.position, p.speed, p.catching, p.throwing, p.agility, p.defense, p.overall()]
                for i, v in enumerate(vals):
                    draw_text(screen, str(v), xs[i], y, self.fonts["sm"], WHITE if i > 1 else color)
            else:
                # 상대팀: 이름·포지션 공개, 개별 스탯 숨김, OVR은 등급으로 표시
                masked = [p.name, p.position, "?", "?", "?", "?", "?", _grade(p.overall())]
                for i, v in enumerate(masked):
                    c = color if i < 2 else (YELLOW if i == 7 else GRAY)
                    draw_text(screen, str(v), xs[i], y, self.fonts["sm"], c)
            y += 26

    def draw(self, screen: pygame.Surface) -> None:
        draw_title(screen, "로스터 확인", self.fonts["lg"])

        # 내 팀
        draw_text(screen, "우리 팀", 60, 105, self.fonts["md"], BLUE)
        self._draw_team(screen, self.gs.player_team, 128, YELLOW, show_stats=True)

        # 상대팀
        sep_y = 128 + 26 + len(self.gs.player_team) * 26 + 18
        draw_text(screen, "상대 팀  (스탯 미공개)", 60, sep_y, self.fonts["md"], RED)
        self._draw_team(screen, self.gs.ai_team, sep_y + 24, RED, show_stats=False)

        # 시작 버튼
        pygame.draw.rect(screen, BLUE, self._btn, border_radius=8)
        draw_text(screen, "게임 시작", SCREEN_W // 2, self._btn.y + 12, self.fonts["md"], WHITE, center=True)
