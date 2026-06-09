"""
FieldRenderer: 정적 필드 배경을 Surface에 한 번 캐싱하고
매 프레임에는 동적 요소만 재드로우.
"""
import pygame
from typing import Optional

from constants import (
    WHITE, GRAY, GOLD, BLUE, YELLOW, GREEN, DARK_GREEN,
    SCREEN_W, FIELD_X, FIELD_Y, FIELD_W, FIELD_H, ENDZONE_W, PLAY_ZONE_W,
    TD_YARDS, MIDFIELD, NO_RUN_ZONE_WIDTH,
)
from ui.renderer import draw_text, yard_to_px

_ORANGE    = (255, 140, 0)
_NRZ_ALPHA = 90

# 야드 레이블이 필드 위쪽에 그려지므로 여백을 포함한 높이
_LABEL_PAD = 26   # FIELD_Y 위쪽 여백
_SURF_H    = FIELD_H + _LABEL_PAD


class FieldRenderer:
    """
    정적 배경(녹색 + 엔드존 + 야드라인)을 Surface에 캐싱.
    draw() 호출마다 동적 요소(NRZ, 퍼스트다운 마커, LOS, 볼)만 재드로우.
    """

    def __init__(self):
        self._static: Optional[pygame.Surface] = None

    # ──────────────────────────────────────────────
    # public
    # ──────────────────────────────────────────────

    def draw(
        self,
        screen: pygame.Surface,
        ball_yard: int,
        yards_to_go: int,
        possession: str,
        crossed_midfield: bool,
        font_sm,
    ) -> None:
        if self._static is None:
            self._static = self._build_static(font_sm)

        # 정적 배경 blit (야드 레이블 포함 영역)
        screen.blit(self._static, (FIELD_X, FIELD_Y - _LABEL_PAD))

        # ── NRZ 반투명 밴드 (동적: possession 변경마다 달라짐) ──
        self._draw_nrz(screen, possession, font_sm)

        # ── 퍼스트다운 마커 ──────────────────────────────────
        fd_yard = ball_yard + yards_to_go if possession == "player" else ball_yard - yards_to_go
        fd_yard = max(0, min(100, fd_yard))
        fd_px   = yard_to_px(fd_yard)
        pygame.draw.line(screen, YELLOW, (fd_px, FIELD_Y), (fd_px, FIELD_Y + FIELD_H), 3)
        label = "TD" if crossed_midfield else "1ST"
        draw_text(screen, label, fd_px, FIELD_Y + FIELD_H + 2, font_sm, YELLOW, center=True)

        # ── 스크리미지 라인 (파란 점선) ──────────────────────
        los_px = yard_to_px(ball_yard)
        for y in range(FIELD_Y, FIELD_Y + FIELD_H, 10):
            pygame.draw.line(screen, BLUE,
                             (los_px, y),
                             (los_px, min(y + 5, FIELD_Y + FIELD_H)), 2)

        # ── 볼 마커 (삼각형) ─────────────────────────────────
        pygame.draw.polygon(screen, GOLD, [
            (los_px,     FIELD_Y - 5),
            (los_px - 8, FIELD_Y - 18),
            (los_px + 8, FIELD_Y - 18),
        ])

    # ──────────────────────────────────────────────
    # private
    # ──────────────────────────────────────────────

    def _build_static(self, font_sm) -> pygame.Surface:
        surf = pygame.Surface((FIELD_W, _SURF_H))
        surf.fill((0, 0, 0))   # 배경은 투명 대신 검정 (레이블 영역)

        field_rect = pygame.Rect(0, _LABEL_PAD, FIELD_W, FIELD_H)

        # 녹색 필드
        pygame.draw.rect(surf, GREEN, field_rect)

        # 엔드존
        pygame.draw.rect(surf, DARK_GREEN, (0, _LABEL_PAD, ENDZONE_W, FIELD_H))
        pygame.draw.rect(surf, DARK_GREEN,
                         (FIELD_W - ENDZONE_W, _LABEL_PAD, ENDZONE_W, FIELD_H))

        # 야드 라인 (10야드마다)
        for yard in range(0, 101, 10):
            rel_px = yard_to_px(yard) - FIELD_X   # 서피스 좌표
            if yard == MIDFIELD:
                pygame.draw.line(surf, WHITE,
                                 (rel_px, _LABEL_PAD),
                                 (rel_px, _LABEL_PAD + FIELD_H), 3)
                draw_text(surf, "50", rel_px, 4, font_sm, WHITE, center=True)
            else:
                pygame.draw.line(surf, WHITE,
                                 (rel_px, _LABEL_PAD),
                                 (rel_px, _LABEL_PAD + FIELD_H), 1)
                draw_text(surf, str(yard), rel_px, 6, font_sm, GRAY, center=True)

        return surf

    def _draw_nrz(self, screen: pygame.Surface, possession: str, font_sm) -> None:
        if possession == "player":
            zones = [
                (MIDFIELD - NO_RUN_ZONE_WIDTH, MIDFIELD),
                (TD_YARDS  - NO_RUN_ZONE_WIDTH, TD_YARDS),
            ]
        else:
            zones = [
                (MIDFIELD, MIDFIELD + NO_RUN_ZONE_WIDTH),
                (0,        NO_RUN_ZONE_WIDTH),
            ]

        for y0, y1 in zones:
            px0 = yard_to_px(y0)
            px1 = yard_to_px(y1)
            w   = max(1, px1 - px0)
            nrz = pygame.Surface((w, FIELD_H), pygame.SRCALPHA)
            nrz.fill((*_ORANGE, _NRZ_ALPHA))
            screen.blit(nrz, (px0, FIELD_Y))
            pygame.draw.rect(screen, _ORANGE, (px0, FIELD_Y, w, FIELD_H), 2)
            draw_text(screen, "NRZ", (px0 + px1) // 2, FIELD_Y + 4,
                      font_sm, _ORANGE, center=True)
