import pygame
from typing import Optional
from .base import BaseScene
from state import GameState
from controller import end_drive, max_downs
from ui.renderer import draw_text, draw_title, draw_scoreboard, draw_field
from constants import GREEN, WHITE, YELLOW, GRAY, SCREEN_W, SCREEN_H

# constants에 없는 색상을 직접 정의
_ORANGE = (255, 140, 0)


class PuntScene(BaseScene):
    """4th down 미드필드 미돌파 시 펀트 or 플레이 선택."""

    def __init__(self, gs: GameState, fonts: dict):
        self.gs    = gs
        self.fonts = fonts

    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        if event.type != pygame.KEYDOWN:
            return None

        gs = self.gs

        if event.key == pygame.K_p:
            # 펀트: 상대방 5야드선에서 시작
            gs.went_for_it = False
            gs.message = "펀트! 상대팀이 자기 5야드선에서 시작합니다"
            return end_drive(gs)

        if event.key == pygame.K_g:
            # 플레이: go-for-it 플래그 세팅 후 전략 선택으로
            gs.went_for_it = True
            return "strategy"

        return None

    def draw(self, screen: pygame.Surface) -> None:
        gs = self.gs
        max_d = max_downs(gs)
        draw_title(screen, f"{max_d}다운! — 펀트 or 플레이?", self.fonts["lg"])
        draw_scoreboard(screen, gs.player_score, gs.ai_score, self.fonts["md"])
        draw_field(screen, gs.ball_yard, gs.yards_to_go, gs.possession,
                   gs.crossed_midfield, self.fonts["sm"])

        mid = SCREEN_H // 2 - 40

        draw_text(screen,
                  f"미드필드까지 {gs.yards_to_go}야드 남음",
                  SCREEN_W // 2, mid - 44,
                  self.fonts["md"], YELLOW, center=True)

        btn_p = pygame.Rect(SCREEN_W // 2 - 230, mid + 10, 210, 54)
        btn_g = pygame.Rect(SCREEN_W // 2 +  20, mid + 10, 210, 54)

        pygame.draw.rect(screen, _ORANGE, btn_p, border_radius=8)
        pygame.draw.rect(screen, GREEN,   btn_g, border_radius=8)

        draw_text(screen, "[P] 펀트",   btn_p.centerx, btn_p.y + 14, self.fonts["md"], WHITE, center=True)
        draw_text(screen, "[G] 플레이", btn_g.centerx, btn_g.y + 14, self.fonts["md"], WHITE, center=True)

        draw_text(screen, "상대 5야드선에서 시작",
                  btn_p.centerx, btn_p.bottom + 6, self.fonts["sm"], GRAY, center=True)
        draw_text(screen, "실패 시 현 위치에서 교체",
                  btn_g.centerx, btn_g.bottom + 6, self.fonts["sm"], GRAY, center=True)
