import pygame
from typing import Callable, Optional
from .base import BaseScene
from state import GameState
from ui.renderer import draw_text, draw_title, draw_scoreboard
from constants import GOLD, RED, GRAY, SCREEN_W, SCREEN_H


class GameoverScene(BaseScene):
    def __init__(self, gs: GameState, fonts: dict, on_restart: Callable):
        self.gs = gs
        self.fonts = fonts
        self.on_restart = on_restart

    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            self.on_restart()
            return "roster"
        return None

    def draw(self, screen: pygame.Surface) -> None:
        gs = self.gs
        draw_title(screen, "경기 종료", self.fonts["lg"])
        draw_scoreboard(screen, gs.player_score, gs.ai_score, self.fonts["md"])

        mid = SCREEN_H // 2
        if gs.player_score > gs.ai_score:
            msg, color = "승리!", GOLD
        elif gs.player_score < gs.ai_score:
            msg, color = "패배", RED
        else:
            msg, color = "무승부", GRAY

        draw_text(screen, msg,              SCREEN_W // 2, mid,      self.fonts["lg"], color, center=True)
        draw_text(screen, "R 키 → 다시 시작", SCREEN_W // 2, mid + 60, self.fonts["sm"], GRAY,  center=True)
