# commanders.py
# 지휘관 능력을 관리하는 파일
# 현재는 야마모토 이소로쿠만 구현

from settings import *
from effects import Shell


class YamamotoCommander:
    def __init__(self):
        self.name = "야마모토 이소로쿠"
        self.subtitle = "해군 연합 함대"

    def call_bombardment(self, x, y, shells):
        # 해안 포격
        # 총 4발, 각 포탄마다 조금씩 늦게 떨어짐
        for i in range(BOMBARDMENT_COUNT):
            delay = 45 + i * 35
            shells.append(Shell(x, y, delay))
NAVY_SQUAD = {
    "id": "yamamoto_navy_squad",
    "name": "일본 제국 해군",
    "icon": "⚓",
    "cost": 0,
    "unit_type": TYPE_INFANTRY,
    "count": 4,

    "hp": 1050,

    "damage": {
        TYPE_INFANTRY: 40,
        TYPE_VEHICLE: 23,
        TYPE_TANK: 13,
        TYPE_BUILDING: 10,
     },

    "attack_delay": 350,
    "attack_range": 60,
    "preferred_range": 40,
    "splash_radius": 0,

    "speed": SPEED_SLOW,
    "can_flank": True,

    "grenade_damage": {
        TYPE_INFANTRY: 350,
        TYPE_VEHICLE: 450,
        TYPE_TANK: 400,
        TYPE_BUILDING: 300,
    },
    "grenade_delay": 10000,
    "grenade_range": 60,
    "grenade_splash_radius": 45,

    "target_priority": [
        TYPE_INFANTRY,
        TYPE_VEHICLE,
        TYPE_TANK,
        TYPE_BUILDING,
    ],

    "abilities": [
        "해군 정신",
        "기관단총 이동사격",
        "대전차 수류탄",
        "수류탄",
    ],

    "is_ranged_infantry": True,
}