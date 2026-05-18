# game.py

import random
import pygame

from settings import *
from cards import CARD_POOL
from buildings import create_default_buildings
from units import create_enemy_infantry, create_units_from_card
from commanders import YamamotoCommander, NAVY_SQUAD
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
        self.draw_pile = CARD_POOL.copy()
        random.shuffle(self.draw_pile)

        self.hand = []
        self.next_card = None
        self.selected_card = None
        self.selected_skill = None

        self.init_hand()
        
        import units
        units.GAME_INSTANCE = self

    def init_hand(self):
        self.hand = []

        for _ in range(4):
            self.hand.append(self.draw_pile.pop(0))

        self.next_card = self.draw_pile[0]

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

        # 건물 그리기
        for building in self.buildings:
            if building.hp > 0:
                building.draw(screen, font)

        # 포격 그리기
        for shell in self.shells:
            shell.draw(screen)

        # -----------------------------
        # 분대 전체 체력 계산
        # 개별 병사가 아니라
        # "분대 총 체력" 기준으로 표시
        # -----------------------------

        squad_totals = {}

        for unit in self.units:
            # -----------------------------
            # 분대 총 체력 계산
            # 개체별 체력은 유지하면서
            # UI만 분대 체력처럼 보이게 함
            # -----------------------------

            if unit.squad_id not in squad_totals:

                squad_totals[unit.squad_id] = [
                    0,
                    unit.card.get(
                        "squad_max_hp",
                        unit.max_hp
                    )
                ]

            # 현재 살아있는 유닛 체력 합산
            squad_totals[unit.squad_id][0] += max(0, unit.hp)
        drawn_squads = set()
                

        # 유닛 그리기
        for unit in self.units:
            unit.draw(screen, font, squad_totals, drawn_squads)

        # 데미지 텍스트
        for text in self.floating_texts:
            text.draw(screen, font)

        draw_placement_preview(
            screen,
            self.selected_card,
            self.selected_skill,
            self.hand
        )

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
        # -----------------------------
        # 생산력 회복 시스템
        #
        # 0~2분:
        # 3초당 생산력 1 회복
        #
        # 2분 이후:
        # 1.5초당 생산력 1 회복
        # -----------------------------

        if now >= COST_ACCEL_TIME:
            recover_time = LATE_COST_RECOVER_TIME
        else:
            recover_time = EARLY_COST_RECOVER_TIME

        if now - self.last_cost_time >= recover_time:
            self.last_cost_time = now

            self.cost = min(
                self.max_cost,
                self.cost + 1
            )

    def recover_command_points(self, now):
        # 지휘력은 22초당 1 회복
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
        used_card = card

        # 다음 카드가 손패로 들어옴
        replacement_card = self.draw_pile.pop(0)
        self.hand[self.selected_card] = replacement_card

        # 사용한 카드는 덱 맨 뒤로 이동
        self.draw_pile.append(used_card)

        # 다음으로 뽑힐 카드 갱신
        self.next_card = self.draw_pile[0]

        self.selected_card = None
        
    def can_place_card(self, card, x, y):
        # 후방 진입로는 대부분의 보병이 배치 가능
        for zone in PLAYER_REAR_ZONES:
            if pygame.Rect(zone).collidepoint(x, y):
                return True

        # 측면 진입로는 can_flank가 True인 유닛만 배치 가능
        if card.get("can_flank", False):
            for zone in PLAYER_FLANK_ZONES:
                if pygame.Rect(zone).collidepoint(x, y):
                    return True

        return False

    def can_place_navy(self, x, y):
        # 해군 스킬은 후방 진입로와 측면 진입로 모두 배치 가능
        for zone in PLAYER_REAR_ZONES:
            if pygame.Rect(zone).collidepoint(x, y):
                return True

        for zone in PLAYER_FLANK_ZONES:
            if pygame.Rect(zone).collidepoint(x, y):
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

            # -----------------------------
            # 야마모토 지휘 스킬 2
            # 일본 제국 해군 분대 소환
            # -----------------------------

            new_units = create_units_from_card(
                NAVY_SQUAD,
                x,
                y,
                PLAYER
            )

            self.units.extend(new_units)

        # 스킬 사용 후 선택 해제
        self.selected_skill = None