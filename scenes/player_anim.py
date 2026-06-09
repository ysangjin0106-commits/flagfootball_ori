"""
키프레임 기반 선수/볼 경로 시스템.

각 선수는 PlayerPath 객체를 가지며,
(frame, (x, y)) 키프레임 사이를 ease-out 보간으로 이동한다.
"""
import math
from typing import List, Tuple, Callable
from data.players import Player

Pos = Tuple[int, int]

# ── 타임라인 (프레임, ANIM_DURATION=90 기준) ─────────────────────
T_SNAP   = 18   # 스냅 완료
T_DROP   = 42   # QB 드롭백 / 핸드오프 완료
T_THROW  = 55   # QB 패스 릴리즈
T_LAND   = 76   # 볼 도착 (캐치 또는 수비)
T_END    = 90


def _ease(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 2


def _lp(p1: Pos, p2: Pos, t: float) -> Pos:
    e = _ease(t)
    return (int(p1[0] + (p2[0] - p1[0]) * e),
            int(p1[1] + (p2[1] - p1[1]) * e))


class PlayerPath:
    """키프레임 목록으로 정의된 선수 이동 경로."""

    def __init__(self, keyframes: List[Tuple[int, Pos]]):
        self._kf = sorted(keyframes)

    def pos(self, frame: int) -> Pos:
        if frame <= self._kf[0][0]:
            return self._kf[0][1]
        if frame >= self._kf[-1][0]:
            return self._kf[-1][1]
        for i in range(len(self._kf) - 1):
            f0, p0 = self._kf[i]
            f1, p1 = self._kf[i + 1]
            if f0 <= frame < f1:
                return _lp(p0, p1, (frame - f0) / (f1 - f0))
        return self._kf[-1][1]


def _sort5(team: List[Player]) -> List[Player]:
    """[QB, WR1, WR2, RB, DB/SLOT] 순서로 재배열."""
    buckets: dict = {"QB": [], "WR": [], "RB": [], "DB": []}
    for p in team:
        buckets.get(p.position, buckets["DB"]).append(p)
    ordered = (buckets["QB"] + buckets["WR"] +
               buckets["RB"] + buckets["DB"])[:5]
    while len(ordered) < 5:
        ordered.append(team[0])
    return ordered


def build_play_anim(
    off_team: List[Player],
    def_team: List[Player],
    los_px:    int,
    mid_y:     int,
    D:         int,          # +1: 오른쪽 진행(플레이어 공격), -1: 왼쪽 진행
    is_run:    bool,
    play_result: str,        # "success" | "big_play" | "failure" | "incomplete"
    target_px:  int,
) -> Tuple[list, list, Callable[[int], Pos]]:
    """
    반환: (off_anim, def_anim, ball_fn)
      off_anim / def_anim : [(Player, PlayerPath, RGB_color), ...]
      ball_fn             : frame -> (x, y)
    """
    off5 = _sort5(off_team)   # [QB, WR1, WR2, RB, SLOT]
    def5 = _sort5(def_team)   # 수비 역할로 재매핑

    # ── 포메이션 시작 위치 ────────────────────────────────────────
    # D=+1: offense는 LOS 왼쪽, defense는 LOS 오른쪽
    qb_s   = (los_px - D * 50,  mid_y)
    wr1_s  = (los_px - D * 8,   mid_y - 120)
    wr2_s  = (los_px - D * 8,   mid_y + 120)
    rb_s   = (los_px - D * 75,  mid_y + 28)
    slot_s = (los_px - D * 8,   mid_y - 55)

    cb1_s  = (los_px + D * 12,  mid_y - 120)   # 코너백 (WR1 커버)
    cb2_s  = (los_px + D * 12,  mid_y + 120)   # 코너백 (WR2 커버)
    lb_s   = (los_px + D * 18,  mid_y)          # 라인배커
    s1_s   = (los_px + D * 70,  mid_y - 45)    # 세이프티
    s2_s   = (los_px + D * 70,  mid_y + 45)    # 세이프티

    if is_run:
        # ── 러닝플레이 ────────────────────────────────────────────
        run_end = (target_px, mid_y + 15)
        stop    = (target_px + D * 14, mid_y + 8)

        qb_path   = PlayerPath([
            (0,       qb_s),
            (T_SNAP,  (los_px - D * 30,  mid_y)),           # 스냅
            (T_DROP,  (los_px - D * 45,  mid_y - 14)),      # 핸드오프 동작
            (T_END,   (los_px - D * 62,  mid_y - 30)),      # 페이크 후 물러남
        ])
        rb_path   = PlayerPath([
            (0,       rb_s),
            (T_DROP,  (los_px - D * 28,  mid_y + 12)),      # 핸드오프 지점
            (T_LAND,  run_end),                               # 돌파
            (T_END,   run_end),
        ])
        wr1_path  = PlayerPath([
            (0,       wr1_s),
            (T_SNAP,  (los_px + D * 10,  mid_y - 110)),     # 블로킹 스템
            (T_END,   (los_px + D * 28,  mid_y - 100)),
        ])
        wr2_path  = PlayerPath([
            (0,       wr2_s),
            (T_SNAP,  (los_px + D * 10,  mid_y + 110)),
            (T_END,   (los_px + D * 28,  mid_y + 100)),
        ])
        slot_path = PlayerPath([
            (0,       slot_s),
            (T_SNAP,  (los_px + D * 22,  mid_y - 42)),      # 디코이 루트
            (T_END,   (los_px + D * 58,  mid_y - 32)),
        ])

        # 수비: RB 수렴
        cb1_path  = PlayerPath([
            (0,       cb1_s),
            (T_DROP,  (los_px + D * 30,  mid_y - 75)),
            (T_END,   stop),
        ])
        cb2_path  = PlayerPath([
            (0,       cb2_s),
            (T_DROP,  (los_px + D * 30,  mid_y + 75)),
            (T_END,   (stop[0], stop[1] + 12)),
        ])
        lb_path   = PlayerPath([
            (0,       lb_s),
            (T_THROW, (los_px + D * 40,  mid_y)),
            (T_END,   stop),
        ])
        s1_path   = PlayerPath([(0, s1_s), (T_END, (stop[0] - D*20, mid_y - 28))])
        s2_path   = PlayerPath([(0, s2_s), (T_END, (stop[0] - D*20, mid_y + 28))])

        def _ball_fn(frame: int) -> Pos:
            # 스냅 전: LOS 중앙, 핸드오프 후: RB 추적
            if frame < T_SNAP:
                return (los_px, mid_y)
            if frame < T_DROP:
                return qb_path.pos(frame)
            return rb_path.pos(frame)

    else:
        # ── 패스플레이 ────────────────────────────────────────────
        big    = (play_result == "big_play")
        failed = play_result in ("failure", "incomplete")

        # 캐치 지점: big_play=WR2 딥, 일반=WR1 슬랜트, 실패=LOS 근처
        if big:
            catch_pos: Pos = (target_px, mid_y + 110)
        elif failed:
            catch_pos = (los_px + D * 40, mid_y - 62)
        else:
            catch_pos = (target_px, mid_y - 62)

        qb_drop = (los_px - D * 100, mid_y)
        qb_path = PlayerPath([
            (0,       qb_s),
            (T_SNAP,  (los_px - D * 60,  mid_y)),
            (T_DROP,  qb_drop),
            (T_END,   qb_drop),
        ])

        # WR1: 슬랜트 루트 (직진 후 안쪽 대각선 컷)
        wr1_cut = (los_px + D * 55,  mid_y - 100)
        wr1_end = catch_pos if not big else (los_px + D * 80, mid_y - 85)
        wr1_path = PlayerPath([
            (0,       wr1_s),
            (T_SNAP,  wr1_s),
            (T_DROP,  wr1_cut),
            (T_LAND,  wr1_end),
            (T_END,   (wr1_end[0] + D * 12, wr1_end[1])),
        ])

        # WR2: 플라이 루트 (직선 딥)
        wr2_end = catch_pos if big else (target_px + D * 35, mid_y + 118)
        wr2_path = PlayerPath([
            (0,       wr2_s),
            (T_SNAP,  wr2_s),
            (T_LAND,  wr2_end),
            (T_END,   (wr2_end[0] + D * 10, wr2_end[1])),
        ])

        # RB: 플레어 루트 (QB 반대편 플랫 공간으로 빠짐)
        rb_path = PlayerPath([
            (0,       rb_s),
            (T_SNAP,  (los_px - D * 50,  mid_y + 20)),
            (T_DROP,  (los_px + D * 15,  mid_y + 68)),
            (T_END,   (los_px + D * 42,  mid_y + 72)),
        ])

        # 슬롯: 크로스 루트 (수평으로 가로지르기)
        slot_path = PlayerPath([
            (0,       slot_s),
            (T_SNAP,  slot_s),
            (T_DROP,  (los_px + D * 52,  mid_y - 18)),
            (T_END,   (los_px + D * 115, mid_y + 22)),
        ])

        # 수비 커버리지
        cb1_end  = (catch_pos[0] - D * 12, catch_pos[1] + 8)
        cb1_path = PlayerPath([
            (0,       cb1_s),
            (T_DROP,  (los_px + D * 48,  mid_y - 108)),
            (T_LAND,  cb1_end),
            (T_END,   cb1_end),
        ])
        cb2_end  = (wr2_end[0] - D * 12, wr2_end[1] - 8)
        cb2_path = PlayerPath([
            (0,       cb2_s),
            (T_LAND,  cb2_end),
            (T_END,   (cb2_end[0] + D * 5, cb2_end[1])),
        ])
        lb_end   = qb_drop if failed else (los_px + D * 35, mid_y)
        lb_path  = PlayerPath([
            (0,       lb_s),
            (T_DROP,  lb_end),
            (T_END,   lb_end),
        ])
        s1_path  = PlayerPath([(0, s1_s), (T_END, (los_px + D * 92, mid_y - 42))])
        s2_path  = PlayerPath([(0, s2_s), (T_END, (los_px + D * 92, mid_y + 42))])

        # 포물선 볼 경로
        throw_pos: Pos = qb_path.pos(T_THROW)
        arc_h = max(25, min(80, abs(catch_pos[0] - throw_pos[0]) // 4))

        def _ball_fn(frame: int) -> Pos:
            if frame < T_SNAP:
                return (los_px, mid_y)
            if frame < T_THROW:
                return qb_path.pos(frame)
            if frame >= T_LAND:
                return catch_pos
            t  = (frame - T_THROW) / (T_LAND - T_THROW)
            if play_result == "incomplete":
                # 반쯤 날아가다 지면으로 떨어짐
                mp = ((throw_pos[0] + catch_pos[0]) // 2,
                      throw_pos[1] - arc_h)
                if t < 0.5:
                    return _lp(throw_pos, mp, t * 2)
                ground = (mp[0] + D * 18, mid_y + 8)
                return _lp(mp, ground, (t - 0.5) * 2)
            bx = int(throw_pos[0] + (catch_pos[0] - throw_pos[0]) * t)
            by = int(throw_pos[1] + (catch_pos[1] - throw_pos[1]) * t
                     - arc_h * math.sin(t * math.pi))
            return (bx, by)

    # ── 결과 조립 ──────────────────────────────────────────────────
    OFF_COLORS = [
        (50,  100, 220),   # QB  (진파랑)
        (80,  160, 255),   # WR1 (하늘파랑)
        (80,  160, 255),   # WR2
        (50,  200, 100),   # RB  (초록)
        (80,  160, 255),   # SLOT
    ]
    off_path_list = [qb_path, wr1_path, wr2_path, rb_path, slot_path]
    def_path_list = [cb1_path, cb2_path, lb_path, s1_path, s2_path]

    off_anim = [(off5[i], off_path_list[i], OFF_COLORS[i]) for i in range(5)]
    def_anim = [(def5[i], def_path_list[i], (220, 50, 50))  for i in range(5)]

    return off_anim, def_anim, _ball_fn
