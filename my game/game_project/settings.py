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

# -----------------------------
# 자원 시스템
# -----------------------------

START_COST = 3
MAX_COST = 10
COST_RECOVER_TIME = 1000  # 1초당 코스트 1 회복

START_COMMAND_POINTS = 1
MAX_COMMAND_POINTS = 5
COMMAND_POINT_RECOVER_TIME = 60000  # 1분당 지휘력 1 회복

# -----------------------------
# 배치 가능 지역
# -----------------------------

# 플레이어가 유닛을 배치할 수 있는 후방 지역
PLAYER_REAR_ZONE = (120, 470, 760, 145)

# 측면 배치 가능 지역
PLAYER_LEFT_FLANK_ZONE = (60, 250, 170, 230)
PLAYER_RIGHT_FLANK_ZONE = (770, 250, 170, 230)

# 적 임시 생성 위치
ENEMY_SPAWN_POINTS = [
    (250, 100),
    (500, 100),
    (750, 100)
]

# -----------------------------
# 지휘관 스킬
# -----------------------------

BOMBARDMENT_COST = 3
BOMBARDMENT_DAMAGE = 3000
BOMBARDMENT_BUILDING_DAMAGE_RATE = 0.1
BOMBARDMENT_RADIUS = 85
BOMBARDMENT_RANDOM_RANGE = 70
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

SPEED_SLOW = 0.75
SPEED_NORMAL = 1.25

# -----------------------------
# 유닛 종류
# -----------------------------

TYPE_INFANTRY = "infantry"
TYPE_VEHICLE = "vehicle"
TYPE_TANK = "tank"
TYPE_BUILDING = "building"