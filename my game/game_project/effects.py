# effects.py
# 포격, 데미지 숫자 같은 시각 효과를 관리하는 파일

import random
import math
import pygame

from settings import *
from utils import draw_text


class FloatingText:
    # 데미지를 입었을 때 위로 떠오르는 숫자 효과
    def __init__(self, text, x, y, color):
        self.text = text
        self.x = x
        self.y = y
        self.color = color
        self.life = 50

    def update(self):
        self.y -= 0.6
        self.life -= 1

    def draw(self, screen, font):
        draw_text(screen, font, self.text, self.x, self.y, self.color)


class Shell:
    # 야마모토의 해안 포격 포탄
    # 랜덤 착탄 + 포탄별 지연 시간 적용
    def __init__(self, x, y, delay):
        self.x = x + random.randint(-BOMBARDMENT_RANDOM_RANGE, BOMBARDMENT_RANDOM_RANGE)
        self.y = y + random.randint(-BOMBARDMENT_RANDOM_RANGE, BOMBARDMENT_RANDOM_RANGE)
        self.delay = delay
        self.timer = 0
        self.exploded = False
        self.radius = BOMBARDMENT_RADIUS
        self.damage = BOMBARDMENT_DAMAGE

    def update(self, units, buildings, floating_texts):
        self.timer += 1

        if self.timer >= self.delay and not self.exploded:
            self.explode(units, buildings, floating_texts)

    def explode(self, units, buildings, floating_texts):
        self.exploded = True

        # 유닛에게는 포격 피해 100%
        for unit in units:
            if unit.hp > 0:
                d = math.hypot(unit.rect.centerx - self.x, unit.rect.centery - self.y)
                if d <= self.radius:
                    unit.take_damage(self.damage, floating_texts)

        # 건물에게는 포격 피해 10%
        for building in buildings:
            if building.hp > 0:
                d = math.hypot(building.rect.centerx - self.x, building.rect.centery - self.y)
                if d <= self.radius:
                    building.take_damage(self.damage * BOMBARDMENT_BUILDING_DAMAGE_RATE, floating_texts)

        floating_texts.append(FloatingText("포격!", self.x - 20, self.y - 40, ORANGE))

    def draw(self, screen):
        if not self.exploded:
            # 착탄 예정 위치 표시
            pygame.draw.circle(screen, ORANGE, (int(self.x), int(self.y)), self.radius, 2)
            pygame.draw.line(screen, ORANGE, (self.x - 10, self.y), (self.x + 10, self.y), 2)
            pygame.draw.line(screen, ORANGE, (self.x, self.y - 10), (self.x, self.y + 10), 2)
        else:
            # 폭발 후 잠깐 보이는 원
            pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), self.radius, 3)