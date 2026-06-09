import pygame
from typing import Optional, List, Tuple
from .base import BaseScene
from state import GameState
from data.players import Player
from ui.renderer import draw_text, draw_title
from constants import (
    WHITE, YELLOW, GOLD, GRAY, RED, BLUE, DARK, PANEL,
    SCREEN_W, SCREEN_H,
)

_ORANGE  = (255, 140,   0)
_GREEN_H = ( 60, 160,  60)   # 하이라이트 녹색

# ── 테이블 컬럼 오프셋 (팀 x_off 기준 상대좌표) ─────────────────
_CX  = [  0,  98, 148, 183, 218, 253, 288, 323]
_HDR = ["이름", "포지션", "SPD", "CAT", "THR", "AGI", "DEF", "OVR"]
_TABLE_W = 352   # 히트박스 기준 행 너비

# ── 팀별 x 오프셋 ─────────────────────────────────────────────
_LEFT  = 20
_RIGHT = 530

# ── Y 레이아웃 ─────────────────────────────────────────────────
_Y_LABEL     = 62
_Y_HEADERS   = 84
_Y_STARTERS  = 106
_ROW_H       = 24
_Y_DIVIDER   = _Y_STARTERS + 5 * _ROW_H + 8   # 234
_Y_BENCH_LBL = _Y_DIVIDER + 10                  # 244
_Y_BENCH     = _Y_BENCH_LBL + _ROW_H            # 268
_Y_HINT      = _Y_BENCH + 5 * _ROW_H + 18       # 418
_Y_BTN       = SCREEN_H - 68


def _stat_color(val: int) -> tuple:
    if val >= 9: return (255, 215,   0)
    if val >= 7: return (100, 220, 100)
    if val >= 6: return WHITE
    return GRAY


def _pos_color(pos: str) -> tuple:
    return {"QB": BLUE, "WR": YELLOW, "RB": _ORANGE, "DB": RED}.get(pos, WHITE)


class RosterScene(BaseScene):
    def __init__(self, gs: GameState, fonts: dict):
        self.gs    = gs
        self.fonts = fonts
        self._btn  = pygame.Rect(SCREEN_W // 2 - 110, _Y_BTN, 220, 46)

        # 교체 선택 상태: ("player"|"ai", bench_idx) or None
        self._sel: Optional[Tuple[str, int]] = None

        # 마우스오버 툴팁 대상
        self._tip_player: Optional[Player] = None
        self._tip_pos: Tuple[int, int]     = (0, 0)

        # 히트 테스트용 rect 목록 (draw() 중 갱신)
        self._ps_rects: List[Tuple[pygame.Rect, int]] = []
        self._as_rects: List[Tuple[pygame.Rect, int]] = []
        self._pb_rects: List[Tuple[pygame.Rect, int]] = []
        self._ab_rects: List[Tuple[pygame.Rect, int]] = []

    # ──────────────────────────────────────────────────────────
    # 이벤트
    # ──────────────────────────────────────────────────────────

    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        gs = self.gs

        if event.type == pygame.MOUSEMOTION:
            self._update_tooltip(event.pos)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos

            if self._btn.collidepoint(mx, my):
                return "strategy"

            # 벤치 클릭 → 선택 / 해제
            for r, i in self._pb_rects:
                if r.collidepoint(mx, my):
                    self._sel = None if self._sel == ("player", i) else ("player", i)
                    return None
            for r, i in self._ab_rects:
                if r.collidepoint(mx, my):
                    self._sel = None if self._sel == ("ai", i) else ("ai", i)
                    return None

            # 선발 클릭 → 교체 실행 (같은 팀 벤치 선수 선택된 경우)
            if self._sel:
                team, bidx = self._sel
                if team == "player":
                    for r, i in self._ps_rects:
                        if r.collidepoint(mx, my):
                            gs.player_team[i], gs.player_bench[bidx] = \
                                gs.player_bench[bidx], gs.player_team[i]
                            self._sel = None
                            return None
                else:
                    for r, i in self._as_rects:
                        if r.collidepoint(mx, my):
                            gs.ai_team[i], gs.ai_bench[bidx] = \
                                gs.ai_bench[bidx], gs.ai_team[i]
                            self._sel = None
                            return None

            self._sel = None   # 빈 곳 클릭 → 선택 해제

        return None

    def _update_tooltip(self, pos: Tuple[int, int]) -> None:
        mx, my = pos
        tip = None
        for group, players in [
            (self._ps_rects, self.gs.player_team),
            (self._as_rects, self.gs.ai_team),
            (self._pb_rects, self.gs.player_bench),
            (self._ab_rects, self.gs.ai_bench),
        ]:
            for r, i in group:
                if r.collidepoint(mx, my):
                    tip = players[i]
        self._tip_player = tip
        self._tip_pos    = pos

    # ──────────────────────────────────────────────────────────
    # 드로우 헬퍼
    # ──────────────────────────────────────────────────────────

    def _draw_headers(self, screen: pygame.Surface, x: int, y: int) -> None:
        for i, h in enumerate(_HDR):
            draw_text(screen, h, x + _CX[i], y, self.fonts["sm"], GOLD)

    def _draw_starter_row(self, screen: pygame.Surface, p: Player,
                          x: int, y: int, name_color: tuple,
                          highlight: bool) -> pygame.Rect:
        row_rect = pygame.Rect(x - 2, y - 2, _TABLE_W, _ROW_H)
        if highlight:
            pygame.draw.rect(screen, (40, 70, 40), row_rect, border_radius=3)
            pygame.draw.rect(screen, _GREEN_H,     row_rect, 1,  border_radius=3)

        vals   = [p.name, p.position, p.speed, p.catching,
                  p.throwing, p.agility, p.defense, p.overall()]
        colors = [name_color, _pos_color(p.position),
                  _stat_color(p.speed), _stat_color(p.catching),
                  _stat_color(p.throwing), _stat_color(p.agility),
                  _stat_color(p.defense), _stat_color(p.overall())]
        for i, (v, c) in enumerate(zip(vals, colors)):
            draw_text(screen, str(v), x + _CX[i], y, self.fonts["sm"], c)
        return row_rect

    def _draw_bench_row(self, screen: pygame.Surface, p: Player,
                        x: int, y: int, selected: bool) -> pygame.Rect:
        row_rect = pygame.Rect(x - 2, y - 2, 200, _ROW_H)
        if selected:
            pygame.draw.rect(screen, (30, 60, 30),  row_rect, border_radius=3)
            pygame.draw.rect(screen, _GREEN_H,       row_rect, 1,  border_radius=3)

        draw_text(screen, f"[{p.position}]", x, y,
                  self.fonts["sm"], _pos_color(p.position))
        draw_text(screen, p.name, x + 52, y, self.fonts["sm"],
                  _GREEN_H if selected else WHITE)
        return row_rect

    def _draw_team_col(self, screen: pygame.Surface,
                       players: List[Player], bench: List[Player],
                       x: int, label: str, name_color: tuple,
                       team_key: str) -> None:
        bench_sel   = self._sel[1] if (self._sel and self._sel[0] == team_key) else None
        has_sel     = bench_sel is not None
        sel_name    = bench[bench_sel].name if has_sel else ""

        draw_text(screen, label, x, _Y_LABEL, self.fonts["md"], name_color)
        self._draw_headers(screen, x, _Y_HEADERS)

        # ── 선발 ──
        starter_rects = []
        for i, p in enumerate(players):
            y = _Y_STARTERS + i * _ROW_H
            r = self._draw_starter_row(screen, p, x, y, name_color, highlight=has_sel)
            starter_rects.append((r, i))

        # ── 구분선 + 교체 선수 레이블 ──
        pygame.draw.line(screen, GRAY, (x, _Y_DIVIDER), (x + _TABLE_W, _Y_DIVIDER), 1)
        bench_label = (f"교체 선수  ←  {sel_name} 선택됨  /  교체할 선발 선수를 클릭"
                       if has_sel else "교체 선수  (이름에 마우스오버 → 스탯 확인 / 클릭 → 교체 선택)")
        draw_text(screen, bench_label, x, _Y_BENCH_LBL, self.fonts["sm"],
                  _GREEN_H if has_sel else GOLD)

        # ── 벤치 ──
        bench_rects = []
        for i, p in enumerate(bench):
            y = _Y_BENCH + i * _ROW_H
            r = self._draw_bench_row(screen, p, x, y,
                                     selected=(self._sel == (team_key, i)))
            bench_rects.append((r, i))

        if team_key == "player":
            self._ps_rects = starter_rects
            self._pb_rects = bench_rects
        else:
            self._as_rects = starter_rects
            self._ab_rects = bench_rects

    def _draw_tooltip(self, screen: pygame.Surface) -> None:
        p  = self._tip_player
        mx, my = self._tip_pos

        lines = [
            (p.name,                                           GOLD),
            (f"포지션: {p.position}",                         _pos_color(p.position)),
            (f"SPD  {p.speed}",                               _stat_color(p.speed)),
            (f"CAT  {p.catching}",                            _stat_color(p.catching)),
            (f"THR  {p.throwing}",                            _stat_color(p.throwing)),
            (f"AGI  {p.agility}",                             _stat_color(p.agility)),
            (f"DEF  {p.defense}",                             _stat_color(p.defense)),
            (f"OVR  {p.overall()}",                           _stat_color(p.overall())),
        ]

        line_h, pad = 20, 10
        w = 160
        h = len(lines) * line_h + pad * 2

        tx = min(mx + 16, SCREEN_W - w - 4)
        ty = max(min(my - h // 2, SCREEN_H - h - 4), 4)

        pygame.draw.rect(screen, (25, 25, 45),
                         (tx, ty, w, h), border_radius=6)
        pygame.draw.rect(screen, GOLD,
                         (tx, ty, w, h), 1, border_radius=6)

        fy = ty + pad
        for text, color in lines:
            draw_text(screen, text, tx + pad, fy, self.fonts["sm"], color)
            fy += line_h

    # ──────────────────────────────────────────────────────────
    # 메인 draw
    # ──────────────────────────────────────────────────────────

    def draw(self, screen: pygame.Surface) -> None:
        gs = self.gs
        draw_title(screen, "로스터 확인  /  경기 전 선수 교체", self.fonts["lg"])

        self._draw_team_col(screen,
                            gs.player_team, gs.player_bench,
                            _LEFT, "우리 팀", YELLOW, "player")
        self._draw_team_col(screen,
                            gs.ai_team, gs.ai_bench,
                            _RIGHT, "상대 팀", RED, "ai")

        # 하단 힌트
        if self._sel is None:
            hint = "벤치 선수를 클릭해 선택 → 교체할 선발 선수를 클릭하면 교체됩니다"
        else:
            team, idx = self._sel
            bench = gs.player_bench if team == "player" else gs.ai_bench
            hint  = f"[ {bench[idx].name} 선택 중 ]  같은 팀 선발 선수를 클릭해 교체 / 재클릭하면 취소"
        draw_text(screen, hint, SCREEN_W // 2, _Y_HINT,
                  self.fonts["sm"], _GREEN_H if self._sel else GRAY, center=True)

        # 시작 버튼
        pygame.draw.rect(screen, BLUE, self._btn, border_radius=8)
        draw_text(screen, "게임 시작", SCREEN_W // 2, self._btn.y + 12,
                  self.fonts["md"], WHITE, center=True)

        # 툴팁 (최상단 레이어)
        if self._tip_player:
            self._draw_tooltip(screen)
