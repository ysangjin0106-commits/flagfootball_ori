import pygame
import sys

from state import GameState, new_state
from scenes import RosterScene, StrategyScene, AnimationScene, ResultScene, GameoverScene, PatScene, PuntScene
from constants import DARK, FPS


class Game:
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.fonts: dict = {
            "lg": pygame.font.SysFont("malgun gothic", 32, bold=True),
            "md": pygame.font.SysFont("malgun gothic", 22),
            "sm": pygame.font.SysFont("malgun gothic", 17),
        }
        self.gs: GameState = new_state()
        self._build_scenes()
        self.scene_name = "roster"

    def _build_scenes(self) -> None:
        gs, fonts = self.gs, self.fonts
        self.scenes: dict = {
            "roster":    RosterScene(gs, fonts),
            "strategy":  StrategyScene(gs, fonts),
            "animation": AnimationScene(gs, fonts),
            "result":    ResultScene(gs, fonts),
            "gameover":  GameoverScene(gs, fonts, self._restart),
            "pat":       PatScene(gs, fonts),
            "punt":      PuntScene(gs, fonts),
        }

    def _restart(self) -> None:
        self.gs = new_state()
        self._build_scenes()

    def run(self, clock: pygame.time.Clock) -> None:
        while True:
            clock.tick(FPS)
            scene = self.scenes[self.scene_name]

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                next_scene = scene.handle_event(event)
                if next_scene:
                    self.scene_name = next_scene

            next_scene = scene.update()
            if next_scene:
                self.scene_name = next_scene

            self.screen.fill(DARK)
            self.scenes[self.scene_name].draw(self.screen)
            pygame.display.flip()
