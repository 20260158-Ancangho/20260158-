# game.py

import random
import pygame

from settings import *
from cards import CARD_POOL
from buildings import create_default_buildings
from units import create_enemy_infantry, create_units_from_card
from commanders import YamamotoCommander
from ui import draw_battlefield, draw_game_ui, draw_placement_preview


class Game:
    def __init__(self):
        self.units = []
        self.buildings = create_default_buildings()
        self.shells = []
        self.floating_texts = []

        self.commander = YamamotoCommander()

        # 일반 카드 코스트
        self.cost = START_COST
        self.max_cost = MAX_COST
        self.last_cost_time = 0

        # 지휘 스킬용 지휘력
        self.command_points = START_COMMAND_POINTS
        self.max_command_points = MAX_COMMAND_POINTS
        self.last_command_time = 0

        self.last_enemy_spawn = 0

        # 카드 덱 / 손패 / 다음 카드
        self.deck = CARD_POOL.copy()
        random.shuffle(self.deck)

        self.hand = []
        self.next_card = None
        self.selected_card = None
        self.selected_skill = None

        self.init_hand()

    def init_hand(self):
        for _ in range(4):
            self.hand.append(self.draw_card())

        self.next_card = self.draw_card()

    def draw_card(self):
        if len(self.deck) == 0:
            self.deck = CARD_POOL.copy()
            random.shuffle(self.deck)

        return self.deck.pop(0)

    def update(self):
        now = pygame.time.get_ticks()

        self.recover_cost(now)
        self.recover_command_points(now)
        self.spawn_enemy_periodically(now)

        for unit in self.units:
            unit.update(now, self.units, self.buildings, self.floating_texts)

        for shell in self.shells:
            shell.update(self.units, self.buildings, self.floating_texts)

        for text in self.floating_texts:
            text.update()

        self.units = [u for u in self.units if u.hp > 0]
        self.shells = [
            s for s in self.shells
            if not (s.exploded and s.timer > s.delay + 20)
        ]
        self.floating_texts = [
            t for t in self.floating_texts
            if t.life > 0
        ]

    def draw(self, screen, font):
        draw_battlefield(screen, font)

        for building in self.buildings:
            if building.hp > 0:
                building.draw(screen, font)

        for shell in self.shells:
            shell.draw(screen)

        for unit in self.units:
            unit.draw(screen, font)

        for text in self.floating_texts:
            text.draw(screen, font)

        draw_placement_preview(screen, self.selected_card, self.selected_skill)

        draw_game_ui(
            screen,
            font,
            self.cost,
            self.max_cost,
            self.command_points,
            self.max_command_points,
            self.hand,
            self.next_card,
            self.selected_card,
            self.selected_skill
        )

    def recover_cost(self, now):
        # 일반 코스트는 1초당 1 회복
        if now - self.last_cost_time >= COST_RECOVER_TIME:
            self.last_cost_time = now
            self.cost = min(self.max_cost, self.cost + 1)

    def recover_command_points(self, now):
        # 지휘력은 1분당 1 회복
        if now - self.last_command_time >= COMMAND_POINT_RECOVER_TIME:
            self.last_command_time = now
            self.command_points = min(self.max_command_points, self.command_points + 1)

    def spawn_enemy_periodically(self, now):
        if now - self.last_enemy_spawn > 2500:
            self.last_enemy_spawn = now
            self.units.append(create_enemy_infantry())

    def select_card(self, index):
        if index < len(self.hand):
            self.selected_card = index
            self.selected_skill = None

    def select_skill(self, skill_name):
        self.selected_skill = skill_name
        self.selected_card = None

    def place_selected(self, x, y):
        if self.selected_card is not None:
            self.place_card(x, y)

        elif self.selected_skill is not None:
            self.use_skill(x, y)

    def place_card(self, x, y):
        card = self.hand[self.selected_card]

        if self.cost < card["cost"]:
            return

        if not self.can_place_card(card, x, y):
            return

        self.cost -= card["cost"]

        new_units = create_units_from_card(card, x, y, PLAYER)
        self.units.extend(new_units)

        # 사용한 카드는 빠지고, 다음 카드가 손패로 들어옴
        self.hand[self.selected_card] = self.next_card
        self.next_card = self.draw_card()

        self.selected_card = None

    def can_place_card(self, card, x, y):
        rear = pygame.Rect(PLAYER_REAR_ZONE)
        left = pygame.Rect(PLAYER_LEFT_FLANK_ZONE)
        right = pygame.Rect(PLAYER_RIGHT_FLANK_ZONE)

        if rear.collidepoint(x, y):
            return True

        if card.get("can_flank", False):
            if left.collidepoint(x, y) or right.collidepoint(x, y):
                return True

        return False

    def use_skill(self, x, y):
        if self.selected_skill == "bombardment":
            if self.command_points < BOMBARDMENT_COST:
                return

            self.command_points -= BOMBARDMENT_COST
            self.commander.call_bombardment(x, y, self.shells)

        elif self.selected_skill == "navy":
            if self.command_points < NAVY_SKILL_COST:
                return

            if not self.can_place_navy(x, y):
                return

            self.command_points -= NAVY_SKILL_COST

            navy_card = {
                "name": "일본 해군",
                "cost": 0,
                "unit_type": TYPE_INFANTRY,
                "count": NAVY_COUNT,
                "hp": NAVY_HP,
                "damage": {
                    TYPE_INFANTRY: NAVY_DAMAGE,
                    TYPE_VEHICLE: 14,
                    TYPE_TANK: 6,
                    TYPE_BUILDING: 18,
                },
                "attack_delay": NAVY_ATTACK_DELAY,
                "attack_range": NAVY_ATTACK_RANGE,
                "splash_radius": 0,
                "speed": NAVY_SPEED,
                "can_flank": True,
                "abilities": []
            }

            self.units.extend(create_units_from_card(navy_card, x, y, PLAYER))

        self.selected_skill = None

    def can_place_navy(self, x, y):
        rear = pygame.Rect(PLAYER_REAR_ZONE)
        left = pygame.Rect(PLAYER_LEFT_FLANK_ZONE)
        right = pygame.Rect(PLAYER_RIGHT_FLANK_ZONE)

        return rear.collidepoint(x, y) or left.collidepoint(x, y) or right.collidepoint(x, y)