import random
import pygame
from typing import Optional
from .base import BaseScene
from state import GameState
from controller import end_drive
from ui.renderer import draw_text, draw_title, draw_scoreboard
from constants import GOLD, GREEN, RED, GRAY, WHITE, YELLOW, BLUE, SCREEN_W, SCREEN_H

# PAT 성공 확률
_PAT1_SUCCESS = 0.90   # 1점 PAT (1야드 스니크)
_PAT2_SUCCESS = 0.45   # 2점 PAT (5야드 플레이)


class PatScene(BaseScene):
    def __init__(self, gs: GameState, fonts: dict):
        self.gs = gs
        self.fonts = fonts
        self._result_msg: Optional[str] = None
        self._next_scene: Optional[str] = None

    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        if self._next_scene:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                self.gs.pat_pending = False
                self._result_msg = None
                n = self._next_scene
                self._next_scene = None
                return n
            return None

        if event.type != pygame.KEYDOWN:
            return None

        gs = self.gs
        scorer = "우리 팀" if gs.possession == "player" else "AI 팀"

        if event.key == pygame.K_1:
            if random.random() < _PAT1_SUCCESS:
                if gs.possession == "player":
                    gs.player_score += 1
                else:
                    gs.ai_score += 1
                self._result_msg = f"{scorer} 1점 PAT 성공! (총 {gs.player_score} vs {gs.ai_score})"
            else:
                self._result_msg = f"1점 PAT 실패! 추가점 없음"
            self._next_scene = end_drive(gs)

        elif event.key == pygame.K_2:
            if random.random() < _PAT2_SUCCESS:
                if gs.possession == "player":
                    gs.player_score += 2
                else:
                    gs.ai_score += 2
                self._result_msg = f"{scorer} 2점 PAT 성공! (총 {gs.player_score} vs {gs.ai_score})"
            else:
                self._result_msg = f"2점 PAT 실패! 추가점 없음"
            self._next_scene = end_drive(gs)

        return None

    def draw(self, screen: pygame.Surface) -> None:
        gs = self.gs
        draw_title(screen, "터치다운! — PAT 선택", self.fonts["lg"])
        draw_scoreboard(screen, gs.player_score, gs.ai_score, self.fonts["md"])

        mid = SCREEN_H // 2 - 40

        if self._result_msg:
            draw_text(screen, self._result_msg, SCREEN_W // 2, mid, self.fonts["md"], GOLD, center=True)
            draw_text(screen, "Enter → 계속", SCREEN_W // 2, mid + 50, self.fonts["sm"], GRAY, center=True)
            return

        # 선택지 표시
        draw_text(screen, gs.message, SCREEN_W // 2, mid - 40, self.fonts["md"], YELLOW, center=True)

        btn1 = pygame.Rect(SCREEN_W // 2 - 220, mid + 10, 200, 50)
        btn2 = pygame.Rect(SCREEN_W // 2 + 20,  mid + 10, 200, 50)

        pygame.draw.rect(screen, BLUE, btn1, border_radius=8)
        pygame.draw.rect(screen, GREEN, btn2, border_radius=8)

        draw_text(screen, "[1] 1점 PAT", btn1.centerx, btn1.y + 14, self.fonts["md"], WHITE, center=True)
        draw_text(screen, "[2] 2점 PAT", btn2.centerx, btn2.y + 14, self.fonts["md"], WHITE, center=True)

        draw_text(screen, "1야드 스니크  성공률 90%",  btn1.centerx, btn1.bottom + 6, self.fonts["sm"], GRAY, center=True)
        draw_text(screen, "5야드 플레이  성공률 45%", btn2.centerx, btn2.bottom + 6, self.fonts["sm"], GRAY, center=True)
