# units.py

import math
import random
import pygame

from settings import *
from effects import FloatingText


class Unit:
    def __init__(self, x, y, side, card_data):
        self.card = card_data
        self.name = card_data["name"]
        self.side = side
        self.unit_type = card_data.get("unit_type", TYPE_INFANTRY)

        self.rect = pygame.Rect(x, y, 26, 26)

        self.max_hp = card_data["hp"]
        self.hp = self.max_hp

        self.damage_table = card_data["damage"]
        self.attack_delay = card_data["attack_delay"]
        self.attack_range = card_data["attack_range"]
        self.splash_radius = card_data.get("splash_radius", 0)

        self.speed = card_data["speed"]
        self.base_speed = card_data["speed"]

        self.last_attack = 0

        self.abilities = card_data.get("abilities", [])

        self.morale = 100
        self.suppressed_timer = 0

        self.is_hidden = "위장" in self.abilities
        self.is_suicide = "자폭" in self.abilities
        self.is_banzai = False

    def draw(self, screen, font):
        if self.side == PLAYER:
            color = BLUE
        else:
            color = RED

        if self.is_hidden:
            color = PURPLE

        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 1)

        hp_ratio = self.hp / self.max_hp
        pygame.draw.rect(screen, RED, (self.rect.x, self.rect.y - 8, self.rect.w, 4))
        pygame.draw.rect(screen, GREEN, (self.rect.x, self.rect.y - 8, self.rect.w * hp_ratio, 4))

        if self.suppressed_timer > 0:
            img = font.render("!", True, ORANGE)
            screen.blit(img, (self.rect.x + 7, self.rect.y - 28))

    def update(self, now, units, buildings, floating_texts):
        if self.hp <= 0:
            return

        self.update_special_state()

        if self.suppressed_timer > 0:
            self.suppressed_timer -= 1

        target = self.find_target(units, buildings)

        if target is None:
            self.move_forward()
            return

        dist = self.distance_to(target)

        # 돌격 능력: 사거리 8칸 정도 안에 적이 있으면 이동속도 보통으로 증가
        if "돌격" in self.abilities or self.is_banzai:
            if dist <= 80:
                self.speed = SPEED_NORMAL
            else:
                self.speed = self.base_speed

        # 야습대는 사거리보다 2칸 정도 가까이 붙으려 함
        preferred_range = self.card.get("preferred_range", self.attack_range)

        if dist <= self.attack_range and dist <= preferred_range + 5:
            self.attack(target, now, units, buildings, floating_texts)
        else:
            self.move_toward(target)

    def update_special_state(self):
        # 일본군 보병: 체력이 절반 이하가 되면 반자이 돌격 발동
        if "반자이 돌격" in self.abilities:
            if self.hp <= self.max_hp * 0.5 and not self.is_banzai:
                self.is_banzai = True
                self.damage_table = self.card["bayonet_damage"]
                self.attack_delay = self.card["bayonet_attack_delay"]
                self.attack_range = self.card["bayonet_range"]

    def find_target(self, units, buildings):
        targets = []

        for unit in units:
            if unit.side != self.side and unit.hp > 0:
                # 위장 유닛은 공격 전까지 타겟이 되지 않음
                if getattr(unit, "is_hidden", False):
                    continue
                targets.append(unit)

        for building in buildings:
            if building.side != self.side and building.hp > 0:
                targets.append(building)

        if not targets:
            return None

        priority = self.card.get("target_priority")

        if priority:
            targets.sort(key=lambda t: (
                priority.index(getattr(t, "unit_type", TYPE_BUILDING))
                if getattr(t, "unit_type", TYPE_BUILDING) in priority else 99,
                self.distance_to(t)
            ))
        else:
            targets.sort(key=lambda t: self.distance_to(t))

        return targets[0]

    def move_forward(self):
        move_speed = self.speed

        if self.suppressed_timer > 0:
            move_speed *= 0.45

        if self.side == PLAYER:
            self.rect.y -= move_speed
        else:
            self.rect.y += move_speed

    def move_toward(self, target):
        move_speed = self.speed

        if self.suppressed_timer > 0:
            move_speed *= 0.45

        dx = target.rect.centerx - self.rect.centerx
        dy = target.rect.centery - self.rect.centery
        dist = max(1, math.hypot(dx, dy))

        self.rect.x += dx / dist * move_speed
        self.rect.y += dy / dist * move_speed

    def attack(self, target, now, units, buildings, floating_texts):
        if now - self.last_attack < self.attack_delay:
            return

        self.last_attack = now

        # 위장 해제
        if self.is_hidden:
            self.is_hidden = False

        target_type = getattr(target, "unit_type", TYPE_BUILDING)
        damage = self.damage_table.get(target_type, self.damage_table[TYPE_INFANTRY])

        if self.splash_radius > 0:
            self.area_damage(target, damage, units, buildings, floating_texts)
        else:
            target.take_damage(damage, floating_texts)

        if self.is_suicide:
            self.hp = 0

    def area_damage(self, target, damage, units, buildings, floating_texts):
        tx = target.rect.centerx
        ty = target.rect.centery

        for unit in units:
            if unit.side != self.side and unit.hp > 0:
                d = math.hypot(unit.rect.centerx - tx, unit.rect.centery - ty)
                if d <= self.splash_radius:
                    unit.take_damage(damage, floating_texts)

        for building in buildings:
            if building.side != self.side and building.hp > 0:
                d = math.hypot(building.rect.centerx - tx, building.rect.centery - ty)
                if d <= self.splash_radius:
                    building.take_damage(damage, floating_texts)

    def reduce_morale(self, amount):
        # 야마토 정신: 사기 저하 면역
        if "야마토 정신" in self.abilities:
            return

        self.morale -= amount

        if self.morale <= 0:
            self.morale = 45
            self.suppressed_timer = 120

    def take_damage(self, amount, floating_texts):
        self.hp -= amount
        floating_texts.append(
            FloatingText(f"-{int(amount)}", self.rect.centerx, self.rect.y, WHITE)
        )

    def distance_to(self, target):
        return math.hypot(
            self.rect.centerx - target.rect.centerx,
            self.rect.centery - target.rect.centery
        )


class MachineGunNest(Unit):
    def __init__(self, x, y, side):
        data = {
            "name": "기관총 진지",
            "hp": 1200,
            "unit_type": TYPE_BUILDING,
            "damage": {
                TYPE_INFANTRY: 8,
                TYPE_VEHICLE: 3,
                TYPE_TANK: 1,
                TYPE_BUILDING: 2,
            },
            "attack_delay": 160,
            "attack_range": 240,
            "splash_radius": 0,
            "speed": 0,
            "abilities": []
        }

        super().__init__(x, y, side, data)
        self.morale_damage = 18

    def move_forward(self):
        pass

    def move_toward(self, target):
        pass


def create_units_from_card(card_data, x, y, side):
    created = []

    for _ in range(card_data["count"]):
        created.append(Unit(
            x + random.randint(-28, 28),
            y + random.randint(-20, 20),
            side,
            card_data
        ))

    return created


def create_enemy_infantry():
    data = {
        "name": "미군 일반 보병",
        "cost": 0,
        "unit_type": TYPE_INFANTRY,
        "count": 1,
        "hp": 500,
        "damage": {
            TYPE_INFANTRY: 15,
            TYPE_VEHICLE: 10,
            TYPE_TANK: 4,
            TYPE_BUILDING: 10,
        },
        "attack_delay": 900,
        "attack_range": 120,
        "splash_radius": 0,
        "speed": 0.8,
        "abilities": []
    }

    x, y = random.choice(ENEMY_SPAWN_POINTS)
    return Unit(x, y, ENEMY, data)