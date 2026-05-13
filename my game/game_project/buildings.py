# buildings.py
# 보조 건물과 주 건물을 관리하는 파일

import pygame

from settings import *
from utils import draw_text
from effects import FloatingText


class Building:
    def __init__(self, x, y, side, name, hp, is_main=False):
        self.rect = pygame.Rect(x, y, 90, 70)
        self.side = side
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.is_main = is_main

    def draw(self, screen, font):
        color = BLUE if self.side == PLAYER else RED

        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)

        # 체력바
        hp_ratio = self.hp / self.max_hp
        pygame.draw.rect(screen, RED, (self.rect.x, self.rect.y - 10, self.rect.w, 6))
        pygame.draw.rect(screen, GREEN, (self.rect.x, self.rect.y - 10, self.rect.w * hp_ratio, 6))

        label = "본부" if self.is_main else "보조"
        draw_text(screen, font, label, self.rect.x + 15, self.rect.y + 20, WHITE)

    def take_damage(self, amount, floating_texts):
        self.hp -= amount
        floating_texts.append(
            FloatingText(f"-{int(amount)}", self.rect.centerx, self.rect.y, YELLOW)
        )

        if self.hp <= 0:
            self.hp = 0


def create_default_buildings():
    # Road to Valor 방식처럼 각 진영마다 보조 건물 2개 + 주 건물 1개 배치
    buildings = []

    # 플레이어 건물
    buildings.append(Building(230, 585, PLAYER, "Player Left Tower", 3500))
    buildings.append(Building(680, 585, PLAYER, "Player Right Tower", 3500))
    buildings.append(Building(455, 610, PLAYER, "Player HQ", 6000, is_main=True))

    # 적 건물
    buildings.append(Building(230, 45, ENEMY, "Enemy Left Tower", 3500))
    buildings.append(Building(680, 45, ENEMY, "Enemy Right Tower", 3500))
    buildings.append(Building(455, 20, ENEMY, "Enemy HQ", 6000, is_main=True))

    return buildings