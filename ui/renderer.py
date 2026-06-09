import pygame
from constants import (
    WHITE, GRAY, GOLD, BLUE, RED, GREEN, DARK_GREEN, YELLOW, PANEL,
    SCREEN_W, FIELD_X, FIELD_Y, FIELD_W, FIELD_H, ENDZONE_W, PLAY_ZONE_W,
    TD_YARDS, MIDFIELD, NO_RUN_ZONE_WIDTH,
)

_ORANGE     = (255, 140,   0)
_NRZ_ALPHA  = 90   # NRZ 반투명도 (0~255)


def draw_text(screen, text: str, x: int, y: int, font, color, center: bool = False):
    surf = font.render(str(text), True, color)
    rect = surf.get_rect()
    if center:
        rect.centerx = x
        rect.top = y
    else:
        rect.left = x
        rect.top  = y
    screen.blit(surf, rect)


def draw_title(screen, text: str, font):
    draw_text(screen, text, SCREEN_W // 2, 20, font, WHITE, center=True)


def draw_scoreboard(screen, player_score: int, ai_score: int, font_md):
    bar = pygame.Rect(0, 55, SCREEN_W, 45)
    pygame.draw.rect(screen, PANEL, bar)
    draw_text(screen, f"우리팀  {player_score}", 200,            68, font_md, BLUE, center=True)
    draw_text(screen, "vs",                     SCREEN_W // 2,  68, font_md, GRAY, center=True)
    draw_text(screen, f"{ai_score}  AI팀",      SCREEN_W - 200, 68, font_md, RED,  center=True)


def yard_to_px(yard: int) -> int:
    return int(FIELD_X + ENDZONE_W + (yard / TD_YARDS) * PLAY_ZONE_W)


def _draw_nrz(screen, possession: str) -> None:
    """현재 공격팀의 No Run Zone 두 구역을 반투명 오렌지로 표시."""
    if possession == "player":
        zones = [
            (MIDFIELD - NO_RUN_ZONE_WIDTH, MIDFIELD),       # 미드필드 직전
            (TD_YARDS  - NO_RUN_ZONE_WIDTH, TD_YARDS),      # 엔드존 직전
        ]
    else:
        zones = [
            (MIDFIELD, MIDFIELD + NO_RUN_ZONE_WIDTH),       # AI: 미드필드 직전
            (0, NO_RUN_ZONE_WIDTH),                         # AI: 엔드존 직전
        ]

    nrz_surf = pygame.Surface((1, FIELD_H), pygame.SRCALPHA)
    for y_start, y_end in zones:
        px_start = yard_to_px(y_start)
        px_end   = yard_to_px(y_end)
        w        = max(1, px_end - px_start)
        surf     = pygame.Surface((w, FIELD_H), pygame.SRCALPHA)
        surf.fill((*_ORANGE, _NRZ_ALPHA))
        screen.blit(surf, (px_start, FIELD_Y))
        # 테두리
        pygame.draw.rect(screen, _ORANGE, (px_start, FIELD_Y, w, FIELD_H), 2)
        # "NRZ" 레이블 (구역 중앙 상단)
    # 레이블은 루프 밖에서 별도 처리하지 않고 draw_field에서 처리


def draw_field(screen, ball_yard: int, yards_to_go: int,
               possession: str, crossed_midfield: bool, font_sm):
    # ── 필드 배경 ──────────────────────────────────────────────
    pygame.draw.rect(screen, GREEN,      (FIELD_X, FIELD_Y, FIELD_W, FIELD_H))
    pygame.draw.rect(screen, DARK_GREEN, (FIELD_X, FIELD_Y, ENDZONE_W, FIELD_H))
    pygame.draw.rect(screen, DARK_GREEN, (FIELD_X + FIELD_W - ENDZONE_W, FIELD_Y, ENDZONE_W, FIELD_H))

    # ── No Run Zone 하이라이트 ─────────────────────────────────
    if possession == "player":
        nrz_zones = [
            (MIDFIELD - NO_RUN_ZONE_WIDTH, MIDFIELD),
            (TD_YARDS  - NO_RUN_ZONE_WIDTH, TD_YARDS),
        ]
    else:
        nrz_zones = [
            (MIDFIELD, MIDFIELD + NO_RUN_ZONE_WIDTH),
            (0,        NO_RUN_ZONE_WIDTH),
        ]
    for y0, y1 in nrz_zones:
        px0 = yard_to_px(y0)
        px1 = yard_to_px(y1)
        w   = max(1, px1 - px0)
        surf = pygame.Surface((w, FIELD_H), pygame.SRCALPHA)
        surf.fill((*_ORANGE, _NRZ_ALPHA))
        screen.blit(surf, (px0, FIELD_Y))
        pygame.draw.rect(screen, _ORANGE, (px0, FIELD_Y, w, FIELD_H), 2)
        # "NRZ" 텍스트
        draw_text(screen, "NRZ", (px0 + px1) // 2, FIELD_Y + 4, font_sm, _ORANGE, center=True)

    # ── 야드 라인 (10야드마다) ──────────────────────────────────
    for yard in range(0, 101, 10):
        px = yard_to_px(yard)
        if yard == MIDFIELD:
            # 미드필드: 굵은 흰 선 + "50" 강조
            pygame.draw.line(screen, WHITE, (px, FIELD_Y), (px, FIELD_Y + FIELD_H), 3)
            draw_text(screen, "50", px, FIELD_Y - 20, font_sm, WHITE, center=True)
        else:
            pygame.draw.line(screen, WHITE, (px, FIELD_Y), (px, FIELD_Y + FIELD_H), 1)
            draw_text(screen, str(yard), px, FIELD_Y - 18, font_sm, GRAY, center=True)

    # ── 퍼스트다운 마커 (노란 실선) ────────────────────────────
    fd_yard = ball_yard + yards_to_go if possession == "player" else ball_yard - yards_to_go
    fd_yard = max(0, min(100, fd_yard))
    fd_px   = yard_to_px(fd_yard)
    pygame.draw.line(screen, YELLOW, (fd_px, FIELD_Y), (fd_px, FIELD_Y + FIELD_H), 3)
    label = "TD" if crossed_midfield else "1ST"
    draw_text(screen, label, fd_px, FIELD_Y + FIELD_H + 2, font_sm, YELLOW, center=True)

    # ── 스크리미지 라인 (파란 점선) ────────────────────────────
    los_px = yard_to_px(ball_yard)
    for y in range(FIELD_Y, FIELD_Y + FIELD_H, 10):
        pygame.draw.line(screen, BLUE, (los_px, y), (los_px, min(y + 5, FIELD_Y + FIELD_H)), 2)

    # ── 볼 마커 (삼각형) ───────────────────────────────────────
    pygame.draw.polygon(screen, GOLD, [
        (los_px,     FIELD_Y - 5),
        (los_px - 8, FIELD_Y - 18),
        (los_px + 8, FIELD_Y - 18),
    ])
