import pygame
from typing import Optional, Callable
from .base import BaseScene
from .player_anim import build_play_anim, T_SNAP, T_DROP, T_THROW, T_LAND
from state import GameState
from controller import apply_play_result
from ui.renderer import draw_text, draw_title, draw_scoreboard, yard_to_px
from ui.field_renderer import FieldRenderer
from constants import (
    WHITE, YELLOW, GRAY, SCREEN_W, FIELD_Y, FIELD_H, ANIM_DURATION
)

_R = 14          # 선수 원 반지름
_BALL_R = 8      # 볼 반지름


def _phase_text(frame: int, off_team, is_run: bool, description: str) -> str:
    qb = next((p.name for p in off_team if p.position == "QB"), off_team[0].name)
    rb = next((p.name for p in off_team if p.position == "RB"), off_team[0].name)
    if frame < T_SNAP:
        return "스냅!"
    if frame < T_DROP:
        return f"{rb} 러싱 시작..." if is_run else f"{qb} 드롭백..."
    if not is_run and frame < T_THROW:
        return f"{qb} 패스 준비..."
    return description


class AnimationScene(BaseScene):
    def __init__(self, gs: GameState, fonts: dict):
        self.gs = gs
        self.fonts = fonts
        self._off_anim: Optional[list] = None
        self._def_anim: Optional[list] = None
        self._ball_fn:  Optional[Callable] = None
        self._field = FieldRenderer()

    # 새 플레이 시작 시 경로 구축
    def _build(self) -> None:
        gs = self.gs
        los_px      = yard_to_px(gs.ball_yard)
        mid_y       = FIELD_Y + FIELD_H // 2
        D           = 1 if gs.possession == "player" else -1
        yards       = gs.anim_result["yards"]  if gs.anim_result else 0
        target_yard = gs.ball_yard + yards * D
        target_px   = yard_to_px(max(0, min(100, target_yard)))
        is_run      = gs.anim_result.get("is_run", False) if gs.anim_result else False
        result      = gs.anim_result["result"]   if gs.anim_result else "success"
        off_team    = gs.player_team if gs.possession == "player" else gs.ai_team
        def_team    = gs.ai_team     if gs.possession == "player" else gs.player_team

        self._off_anim, self._def_anim, self._ball_fn = build_play_anim(
            off_team, def_team,
            los_px, mid_y, D,
            is_run, result, target_px,
        )

    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
            self.gs.anim_frame = ANIM_DURATION   # 즉시 완료로 점프
        return None

    def update(self) -> Optional[str]:
        self.gs.anim_frame += 1
        if self.gs.anim_frame >= ANIM_DURATION:
            self._off_anim = None   # 다음 플레이를 위해 초기화
            return apply_play_result(self.gs)
        return None

    def draw(self, screen: pygame.Surface) -> None:
        gs    = self.gs
        frame = gs.anim_frame

        # 첫 프레임에 경로 구축
        if self._off_anim is None:
            self._build()

        draw_title(screen, "플레이 진행 중...", self.fonts["lg"])
        draw_scoreboard(screen, gs.player_score, gs.ai_score, self.fonts["md"])
        self._field.draw(screen, gs.ball_yard, gs.yards_to_go,
                         gs.possession, gs.crossed_midfield, self.fonts["sm"])

        off_team = gs.player_team if gs.possession == "player" else gs.ai_team
        is_run   = gs.anim_result.get("is_run", False) if gs.anim_result else False
        desc     = gs.anim_result["description"] if gs.anim_result else ""

        # ── 수비팀 (하단 레이어) ────────────────────────────────
        for player, path, color in self._def_anim:
            px, py = path.pos(frame)
            pygame.draw.circle(screen, color, (px, py), _R)
            pygame.draw.circle(screen, (160, 20, 20), (px, py), _R, 2)
            draw_text(screen, player.position[:2], px, py - 8,
                      self.fonts["sm"], WHITE, center=True)

        # ── 공격팀 (상단 레이어) ────────────────────────────────
        for player, path, color in self._off_anim:
            px, py = path.pos(frame)
            pygame.draw.circle(screen, color, (px, py), _R)
            pygame.draw.circle(screen, (20, 60, 180), (px, py), _R, 2)
            draw_text(screen, player.position[:2], px, py - 8,
                      self.fonts["sm"], WHITE, center=True)

        # ── 볼 ─────────────────────────────────────────────────
        bx, by = self._ball_fn(frame)
        pygame.draw.circle(screen, YELLOW, (bx, by), _BALL_R)
        pygame.draw.circle(screen, (200, 160, 0), (bx, by), _BALL_R, 2)

        # ── 단계별 텍스트 ────────────────────────────────────────
        txt = _phase_text(frame, off_team, is_run, desc)
        if txt:
            draw_text(screen, txt, SCREEN_W // 2,
                      FIELD_Y + FIELD_H + 14, self.fonts["md"], WHITE, center=True)
