# buildings.py

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
        self.unit_type = TYPE_BUILDING

    def draw(self, screen, font):
        color = BLUE if self.side == PLAYER else RED

        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 2)

        hp_ratio = self.hp / self.max_hp
        pygame.draw.rect(screen, RED, (self.rect.x, self.rect.y - 10, self.rect.w, 6))
        pygame.draw.rect(screen, GREEN, (self.rect.x, self.rect.y - 10, self.rect.w * hp_ratio, 6))

        label = "주 건물" if self.is_main else "보조"
        draw_text(screen, font, label, self.rect.x + 10, self.rect.y + 22, WHITE)

    def take_damage(self, amount, floating_texts):
        self.hp -= amount
        floating_texts.append(
            FloatingText(f"-{int(amount)}", self.rect.centerx, self.rect.y, YELLOW)
        )

        if self.hp <= 0:
            self.hp = 0


def create_default_buildings():
    buildings = []

    # 플레이어 건물
    buildings.append(Building(*PLAYER_LEFT_TOWER_POS, PLAYER, "Player Left Tower", 3500))
    buildings.append(Building(*PLAYER_RIGHT_TOWER_POS, PLAYER, "Player Right Tower", 3500))
    buildings.append(Building(*PLAYER_HQ_POS, PLAYER, "Player HQ", 6000, is_main=True))

    # 적 건물
    buildings.append(Building(*ENEMY_LEFT_TOWER_POS, ENEMY, "Enemy Left Tower", 3500))
    buildings.append(Building(*ENEMY_RIGHT_TOWER_POS, ENEMY, "Enemy Right Tower", 3500))
    buildings.append(Building(*ENEMY_HQ_POS, ENEMY, "Enemy HQ", 6000, is_main=True))

    return buildings