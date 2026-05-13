# cards.py
# 카드 데이터만 모아둔 파일
# 나중에 밸런스 조정은 여기서 하면 됨

from settings import *

CARD_POOL = [
    {
        "id": "japanese_infantry",
        "name": "일본군 보병",
        "cost": 1,
        "unit_type": TYPE_INFANTRY,
        "count": 6,
        "hp": 342,
        "damage": {
            TYPE_INFANTRY: 75,
            TYPE_VEHICLE: 42,
            TYPE_TANK: 11,
            TYPE_BUILDING: 35,
        },
        "bayonet_damage": {
            TYPE_INFANTRY: 200,
            TYPE_VEHICLE: 23,
            TYPE_TANK: 3,
            TYPE_BUILDING: 42,
        },
        "attack_delay": 1500,
        "bayonet_attack_delay": 1200,
        "attack_range": 80,
        "bayonet_range": 20,
        "splash_radius": 0,
        "speed": SPEED_SLOW,
        "can_flank": False,
        "abilities": ["반자이 돌격"],
    },

    {
        "id": "suicide_soldier",
        "name": "자폭병",
        "cost": 3,
        "unit_type": TYPE_INFANTRY,
        "count": 1,
        "hp": 704,
        "damage": {
            TYPE_INFANTRY: 896,
            TYPE_VEHICLE: 960,
            TYPE_TANK: 1026,
            TYPE_BUILDING: 680,
        },
        "attack_delay": 800,
        "attack_range": 10,
        "splash_radius": 60,
        "speed": SPEED_SLOW,
        "can_flank": False,
        "abilities": ["야마토 정신", "돌격", "자폭"],
    },

    {
        "id": "night_raiders",
        "name": "야습대",
        "cost": 4,
        "unit_type": TYPE_INFANTRY,
        "count": 4,
        "hp": 574,
        "damage": {
            TYPE_INFANTRY: 34,
            TYPE_VEHICLE: 23,
            TYPE_TANK: 7,
            TYPE_BUILDING: 20,
        },
        "attack_delay": 400,
        "attack_range": 60,
        "preferred_range": 40,
        "splash_radius": 0,
        "speed": SPEED_SLOW,
        "can_flank": True,
        "abilities": ["위장", "매복"],
    },

    {
        "id": "lunge_mine_soldier",
        "name": "자돌 폭뢰병",
        "cost": 2,
        "unit_type": TYPE_INFANTRY,
        "count": 3,
        "hp": 460,
        "damage": {
            TYPE_INFANTRY: 460,
            TYPE_VEHICLE: 950,
            TYPE_TANK: 840,
            TYPE_BUILDING: 530,
        },
        "attack_delay": 500,
        "attack_range": 20,
        "splash_radius": 40,
        "speed": SPEED_SLOW,
        "can_flank": False,
        "target_priority": [TYPE_TANK, TYPE_VEHICLE, TYPE_BUILDING, TYPE_INFANTRY],
        "abilities": ["자폭", "돌격", "대전차병"],
    },
]