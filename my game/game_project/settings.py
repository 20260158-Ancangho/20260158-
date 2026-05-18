# settings.py

WIDTH = 1000
HEIGHT = 700
FPS = 60

STATE_SELECT = "select"
STATE_GAME = "game"

PLAYER = "player"
ENEMY = "enemy"

WHITE = (240, 240, 240)
BLACK = (20, 20, 20)
GRAY = (120, 120, 120)
DARK = (40, 40, 40)
RED = (200, 60, 60)
BLUE = (60, 120, 220)
GREEN = (70, 180, 90)
YELLOW = (230, 210, 80)
ORANGE = (230, 150, 60)
PURPLE = (150, 90, 220)

#탈것 시스템
BICYCLE_DISMOUNT_DELAY = 250

# -----------------------------
# 자원 시스템
# -----------------------------

# -----------------------------
# 생산력 시스템
# -----------------------------

START_COST = 3
MAX_COST = 10

# 시작~2분까지 3초당 생산력 1
EARLY_COST_RECOVER_TIME = 3000

# 2분 이후 1.5초당 생산력 1
LATE_COST_RECOVER_TIME = 1500

# 생산력 가속 시작 시간
COST_ACCEL_TIME = 120000

# -----------------------------
# 지휘력 시스템
# -----------------------------

START_COMMAND_POINTS = 0
MAX_COMMAND_POINTS = 5

# 22초당 지휘력 1 회복
COMMAND_POINT_RECOVER_TIME = 22000

# -----------------------------
# 맵 구조
# 중앙에는 건물이 있고,
# 실제 유닛 진입은 좌우 도로에서 이루어짐
# -----------------------------

# 왼쪽/오른쪽 도로
LEFT_ROAD_X = 285
RIGHT_ROAD_X = 715

ROAD_WIDTH = 150

# 후방 진입로 4개
# Road to Valor처럼 플레이어 본진 쪽에서 나오는 기본 배치 지점
PLAYER_REAR_ZONES = [
    (225, 505, 150, 80),   # 왼쪽 후방 진입로
    (625, 505, 150, 80),   # 오른쪽 후방 진입로
]

# 측면 진입로 2개
# 보조 건물보다 살짝 위쪽, 옆에서 유닛이 등장하는 느낌
PLAYER_FLANK_ZONES = [
    (70, 320, 115, 90),    # 왼쪽 측면 진입
    (815, 320, 115, 90),   # 오른쪽 측면 진입
]

# 적 임시 생성 위치
ENEMY_SPAWN_POINTS = [
    (260, 100),
    (720, 100),
]

# -----------------------------
# 건물 위치
# -----------------------------

PLAYER_LEFT_TOWER_POS = (245, 545)
PLAYER_RIGHT_TOWER_POS = (665, 545)
PLAYER_HQ_POS = (455, 590)

ENEMY_LEFT_TOWER_POS = (245, 80)
ENEMY_RIGHT_TOWER_POS = (665, 80)
ENEMY_HQ_POS = (455, 35)

# -----------------------------
# 지휘관 스킬
# -----------------------------

BOMBARDMENT_COST = 3
BOMBARDMENT_DAMAGE = 3000
BOMBARDMENT_BUILDING_DAMAGE_RATE = 0.1
BOMBARDMENT_RADIUS = 85
BOMBARDMENT_RANDOM_RANGE = 100
BOMBARDMENT_COUNT = 4

NAVY_SKILL_COST = 2
NAVY_COUNT = 6
NAVY_HP = 650
NAVY_DAMAGE = 22
NAVY_ATTACK_DELAY = 520
NAVY_SPEED = 1.6
NAVY_ATTACK_RANGE = 95

# -----------------------------
# 이동속도
# -----------------------------

SPEED_SLOW = 0.6
SPEED_NORMAL = 1.1
SPEED_FAST = 2.1

# -----------------------------
# 유닛 종류
# -----------------------------

TYPE_INFANTRY = "infantry"
TYPE_VEHICLE = "vehicle"
TYPE_TANK = "tank"
TYPE_BUILDING = "building"

# -----------------------------
# 분대 / 보병 표시 설정
# -----------------------------

INFANTRY_SIZE = 6
SQUAD_ICON_SIZE = 18
OFFICER_AURA_RANGE = 110