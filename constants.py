# 색상
WHITE      = (255, 255, 255)
BLACK      = (0,   0,   0)
GREEN      = (34,  139, 34)
DARK_GREEN = (20,  90,  20)
YELLOW     = (255, 220, 0)
RED        = (220, 50,  50)
BLUE       = (50,  100, 220)
GRAY       = (180, 180, 180)
DARK       = (30,  30,  30)
PANEL      = (20,  20,  40)
GOLD       = (255, 200, 50)

# 화면
SCREEN_W, SCREEN_H = 1024, 768

# 필드
FIELD_X, FIELD_Y = 50,  150
FIELD_W, FIELD_H = 924, 450
ENDZONE_W        = 80
PLAY_ZONE_W      = FIELD_W - ENDZONE_W * 2

# 게임 규칙
TD_YARDS             = 100
TOTAL_POSSESSIONS    = 4

# 필드 구역
MIDFIELD             = 50
NO_RUN_ZONE_WIDTH    = 5   # 미드필드·엔드존 앞 5야드

# 공격 시작 위치
PLAYER_START_YARD    = 5
AI_START_YARD        = 95

# 2구간 다운 시스템
DOWNS_BEFORE_MID     = 4   # 미드필드 돌파까지 최대 다운
DOWNS_AFTER_MID      = 3   # 터치다운까지 최대 다운

# 타이밍
FPS           = 60
ANIM_DURATION = 90
