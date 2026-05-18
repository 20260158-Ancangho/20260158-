# units.py

import math
import random
import pygame
import os

GAME_INSTANCE = None

from settings import *
from effects import FloatingText


_next_squad_id = 1

def get_next_squad_id():
    global _next_squad_id
    value = _next_squad_id
    _next_squad_id += 1
    return value


class Unit:
    def __init__(self, x, y, side, card_data, squad_id=None, member_index=0):
        self.card = card_data
        self.name = card_data["name"]
        self.side = side
        self.unit_type = card_data.get("unit_type", TYPE_INFANTRY)

        size = INFANTRY_SIZE if self.unit_type == TYPE_INFANTRY else 26
        self.rect = pygame.Rect(x, y, size, size)
        
        self.x = float(x)
        self.y = float(y)

        self.squad_id = squad_id
        self.member_index = member_index
        self.icon = card_data.get("icon", "?")
        
        # 이 병사가 현재 수류탄 담당인지 여부
        self.is_grenadier = (
            self.member_index ==
            self.card.get("grenadier_index", -1)
        )
        
        # 어느 라인에서 소환됐는지 기록
        # left / right / center 중 하나
        self.lane = card_data.get("lane", "center")

        self.max_hp = card_data["hp"]
        self.hp = self.max_hp

        self.damage_table = card_data["damage"].copy()
        self.attack_delay = card_data["attack_delay"]
        self.attack_range = card_data["attack_range"]
        self.splash_radius = card_data.get("splash_radius", 0)

        self.speed = card_data["speed"]
        self.base_speed = card_data["speed"]

        self.last_attack = 0
        
        self.frame_index = 0
        self.last_frame_time = 0
        self.sprite_frames = {}
        self.direction = "up_right"

        self.abilities = card_data.get("abilities", []).copy()

        self.morale = 100
        self.suppressed_timer = 0

        self.is_hidden = "위장" in self.abilities
        self.is_suicide = "자폭" in self.abilities
        self.banzai_active = False

        self.is_ranged_infantry = card_data.get("is_ranged_infantry", False)
        self.converted_to_melee = False
        
        # 콜인 진입 상태
        self.is_calling_in = False
        self.call_in_target = None
        
        # -----------------------------
        # 장교 스프라이트 애니메이션 기본값
        # 모든 유닛이 일단 가지고 있게 해두면 오류 방지 가능
        # -----------------------------

        self.frame_index = 0
        self.last_frame_time = 0
        self.sprite_frames = {}

        if self.name == "장교":
            self.load_officer_up_sprites()
        
        self.animation_state = "idle"
        
        # 자전거 보병 전용 상태
        self.is_on_bicycle = "자전거" in self.abilities
        self.dismounting = False
        self.dismount_start_time = 0

        if self.is_on_bicycle:
            self.speed = self.card.get("bicycle_speed", SPEED_FAST)

        # 보조무기 수류탄
        self.last_grenade_time = 0
        
        # 현재 바라보는 방향
        self.direction = "up_right"
    
    def load_officer_up_sprites(self):
        self.sprite_frames = {}

        load_targets = {
            "up_right": {
                "base": os.path.join("assets", "officer_up_right_sprites"),
                "folders": {
                    "idle": "idle_up_right",
                    "move": "move_up_right",
                    "charge": "charge_up_right",
                }
            },
            "up": {
                "base": os.path.join("assets", "officer_up_sprites"),
                "folders": {
                    "idle": "idle",
                    "move": "move",
                    "charge": "charge",
                }
            }
        }

        for direction, info in load_targets.items():
            self.sprite_frames[direction] = {}

            for state, folder_name in info["folders"].items():
                folder = os.path.join(info["base"], folder_name)

                frames = []

                if not os.path.exists(folder):
                    print("장교 스프라이트 폴더 없음:", folder)
                    self.sprite_frames[direction][state] = []
                    continue

                files = sorted([
                    f for f in os.listdir(folder)
                    if f.endswith(".png")
                ])

                for filename in files:
                    path = os.path.join(folder, filename)

                    img = pygame.image.load(path).convert_alpha()
                    img = pygame.transform.smoothscale(img, (22, 30))
                    frames.append(img)

                self.sprite_frames[direction][state] = frames
            
    def draw_officer_sprite(self, screen, font, squad_totals=None, drawn_squads=None):
        state = "idle"

        if "돌격" in self.abilities and self.speed >= SPEED_NORMAL:
            state = "charge"
        elif self.animation_state == "move":
            state = "move"

        direction = self.direction

        # 왼쪽 위는 오른쪽 위 스프라이트를 좌우반전해서 사용
        flip_x = False

        if direction == "up_left":
            direction = "up_right"
            flip_x = True

        # 현재 보유한 방향이 아니면 up으로 fallback
        if direction not in self.sprite_frames:
            direction = "up"

        frames = self.sprite_frames.get(direction, {}).get(state, [])

        if len(frames) == 0:
            pygame.draw.rect(screen, BLUE if self.side == PLAYER else RED, self.rect)
            pygame.draw.rect(screen, WHITE, self.rect, 1)
            return

        now = pygame.time.get_ticks()

        if now - self.last_frame_time > 90:
            self.last_frame_time = now
            self.frame_index = (self.frame_index + 1) % len(frames)

        frame = frames[self.frame_index % len(frames)]

        if flip_x:
            frame = pygame.transform.flip(frame, True, False)

        rect = frame.get_rect(center=self.rect.center)
        screen.blit(frame, rect)

        if squad_totals is not None and drawn_squads is not None:
            if self.squad_id is not None and self.squad_id not in drawn_squads:
                drawn_squads.add(self.squad_id)

                total_hp, total_max_hp = squad_totals[self.squad_id]
                hp_text = font.render(
                    f"{self.icon} {int(total_hp)}/{int(total_max_hp)}",
                    True,
                    WHITE
                )
                screen.blit(hp_text, (self.rect.x - 10, self.rect.y - 28))

    def draw(self, screen, font, squad_totals=None, drawn_squads=None):
        
        if self.name == "장교" and self.sprite_frames:
            self.draw_officer_sprite(
                screen,
                font,
                squad_totals,
                drawn_squads
            )
            return

        color = BLUE if self.side == PLAYER else RED

        if self.is_hidden:
            color = PURPLE
            
        if self.is_on_bicycle:
            color = (80, 200, 220)

        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, BLACK, self.rect, 1)

        # 분대 전체 체력 + 아이콘 표시
        if squad_totals is not None and drawn_squads is not None:
            if self.squad_id is not None and self.squad_id not in drawn_squads:
                drawn_squads.add(self.squad_id)

                total_hp, total_max_hp = squad_totals[self.squad_id]
                text = f"{self.icon} {int(total_hp)}/{int(total_max_hp)}"
                img = font.render(text, True, WHITE)

                screen.blit(img, (self.rect.x - 8, self.rect.y - 28))

        if self.suppressed_timer > 0:
            img = font.render("!", True, ORANGE)
            screen.blit(img, (self.rect.x + 2, self.rect.y - 42))
            

    def update(self, now, units, buildings, floating_texts):
        if self.hp <= 0:
            return
        
        if self.is_calling_in:
            self.move_to_call_in_target()
            self.resolve_unit_collision(units)
            self.prevent_center_building_crossing()
            return
        
        # -----------------------------
        # 기본 애니메이션 상태
        # 이동/공격 시 아래에서 바뀜
        # -----------------------------
        self.animation_state = "idle"

        self.update_special_state(units)
        self.update_officer_aura(units)

        if self.suppressed_timer > 0:
            self.suppressed_timer -= 1

        target = self.find_target(units, buildings)

        if target is None:
            self.move_forward()
            return

        dist = self.distance_to(target)
        
        # -----------------------------
        # 자전거 보병 하차 처리
        # 적과 조우하면 0.25초 뒤 자전거에서 내려 전투 상태가 됨
        # -----------------------------

        if self.is_on_bicycle:
            # 자신의 공격 사거리 안에 적이 들어왔을 때만 하차
            if dist > self.attack_range:
                self.speed = self.card.get("bicycle_speed", SPEED_FAST)
                
                #적이 사거리 밖이면 자전거 탄 상태로 적에게 접근
                self.move_toward(target)
                self.resolve_unit_collision(units)
                self.prevent_center_building_crossing()
                return

            # 사거리 안에 들어오면 하차 시작
            if not self.dismounting:
                self.dismounting = True
                self.dismount_start_time = now
                self.speed = 0
                return

            # 하차 딜레이
            if now - self.dismount_start_time < BICYCLE_DISMOUNT_DELAY:
                return

            # 하차 완료
            self.is_on_bicycle = False
            self.dismounting = False
            self.speed = self.base_speed

        if "돌격" in self.abilities or self.banzai_active:
            if dist <= 80:
                self.speed = SPEED_NORMAL
            else:
                self.speed = self.base_speed

        preferred_range = self.card.get("preferred_range", self.attack_range)

        if dist <= self.attack_range and dist <= preferred_range + 5:
            self.attack(target, now, units, buildings, floating_texts)

            # 공격 중에도 겹치면 밀려나게 함
            self.resolve_unit_collision(units)
            self.prevent_center_building_crossing()
        else:
            self.move_toward(target)
            self.resolve_unit_collision(units)
            self.prevent_center_building_crossing()
            
        self.resolve_unit_collision(units)
        self.prevent_center_building_crossing()
        
            
    def resolve_unit_collision(self, units):
        # 유닛끼리 겹치면 양쪽을 서로 반대 방향으로 밀어냄

        for other in units:
            if other is self:
                continue

            if other.hp <= 0:
                continue

            dx = self.x - other.x
            dy = self.y - other.y
            dist = math.hypot(dx, dy)

            min_dist = 15  # 보병 크기 기준 충돌 거리

            if dist == 0:
                dx = random.choice([-1, 1])
                dy = random.choice([-1, 1])
                dist = 1

            if dist < min_dist:
                overlap = min_dist - dist

                push_x = dx / dist * overlap * 0.5
                push_y = dy / dist * overlap * 0.5

                self.x += push_x
                self.y += push_y

                other.x -= push_x
                other.y -= push_y

                self.rect.x = int(self.x)
                self.rect.y = int(self.y)

                other.rect.x = int(other.x)
                other.rect.y = int(other.y)

    def update_special_state(self, units):
        # -----------------------------
        # 일본군 보병: 반자이 돌격
        # 개체 체력이 아니라 분대 총 체력 기준
        # -----------------------------

        if "반자이 돌격" not in self.abilities:
            return

        if self.squad_id is None:
            return

        squad_hp = 0
        squad_max_hp = self.card.get(
            "squad_max_hp",
            self.card["hp"] * self.card["count"]
        )

        for unit in units:
            if unit.squad_id == self.squad_id:
                squad_hp += max(0, unit.hp)

        # 분대 총 체력이 50% 이하가 되면 분대 전체 반자이 발동
        if squad_hp <= squad_max_hp * 0.5:
            self.card["banzai_active"] = True

        if self.card.get("banzai_active", False) and not self.banzai_active:
            self.banzai_active = True

            self.convert_to_melee(
                self.card["bayonet_damage"],
                self.card["bayonet_attack_delay"],
                self.card["bayonet_range"]
            )
                    
    def update_officer_aura(self, units):
        # 장교 특수 능력:
        # 주변 원거리 보병을 근접 보병으로 바꾸고,
        # 주변 보병에게 돌격 능력을 부여함.
        if self.name != "장교":
            return

        for unit in units:
            if unit.side != self.side:
                continue

            if unit.hp <= 0:
                continue

            if unit is self:
                continue

            if unit.unit_type != TYPE_INFANTRY:
                continue

            if self.distance_to(unit) > OFFICER_AURA_RANGE:
                continue

            if "돌격" not in unit.abilities:
                unit.abilities.append("돌격")

            if unit.is_ranged_infantry and not unit.converted_to_melee:
                # 소총 계열은 총검, 연발 무기 계열은 나이프라는 설정.
                # 현재 코드는 둘 다 근접 보병화로 처리.
                melee_damage = {
                    TYPE_INFANTRY: max(unit.damage_table.get(TYPE_INFANTRY, 0), 160),
                    TYPE_VEHICLE: max(unit.damage_table.get(TYPE_VEHICLE, 0), 20),
                    TYPE_TANK: max(unit.damage_table.get(TYPE_TANK, 0), 3),
                    TYPE_BUILDING: max(unit.damage_table.get(TYPE_BUILDING, 0), 35),
                }

                unit.convert_to_melee(
                    melee_damage,
                    1000,
                    20
                )

    def convert_to_melee(self, new_damage, new_attack_delay, new_attack_range):
        self.damage_table = new_damage.copy()
        self.attack_delay = new_attack_delay
        self.attack_range = new_attack_range
        self.converted_to_melee = True
        self.is_ranged_infantry = False

    def find_target(self, units, buildings):
        targets = []

        for unit in units:
            if unit.side != self.side and unit.hp > 0:
                if getattr(unit, "is_hidden", False):
                    continue

            # 다른 라인에 있는 적은 무시
            # 오른쪽 라인 유닛이 중앙 건물을 뚫고 왼쪽으로 가는 문제 방지
                if getattr(unit, "lane", None) != self.lane:
                    continue

                target_type = getattr(unit, "unit_type", TYPE_INFANTRY)
                if self.damage_table.get(target_type, 0) <= 0:
                    continue

                targets.append(unit)

        for building in buildings:
            if building.side != self.side and building.hp > 0:
                if self.damage_table.get(TYPE_BUILDING, 0) <= 0:
                    continue

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
            self.y -= move_speed
            self.last_dx = 0
            self.last_dy = -1
        else:
            self.y += move_speed
            self.last_dx = 0
            self.last_dy = 1

        self.animation_state = "move"

        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

    def move_toward(self, target):
        move_speed = self.speed

        if self.suppressed_timer > 0:
            move_speed *= 0.45
        
        dx = target.rect.centerx - self.rect.centerx
        dy = target.rect.centery - self.rect.centery
        
        dist = max(1, math.hypot(dx, dy))
        
        self.update_direction(
            target.rect.centerx,
            target.rect.centery
        )

        self.last_dx = dx / dist
        self.last_dy = dy / dist

        self.x += self.last_dx * move_speed
        self.y += self.last_dy * move_speed

        self.animation_state = "move"

        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

    def attack(self, target, now, units, buildings, floating_texts):
        if now - self.last_attack < self.attack_delay:
            return

        self.last_attack = now
        self.animation_state = "attack"

        dx = target.rect.centerx - self.rect.centerx
        dy = target.rect.centery - self.rect.centery
        dist = max(1, math.hypot(dx, dy))
        self.last_dx = dx / dist
        self.last_dy = dy / dist

        if self.is_hidden:
            self.is_hidden = False

        target_type = getattr(target, "unit_type", TYPE_BUILDING)
        damage = self.damage_table.get(target_type, 0)

        if damage <= 0:
            return

        if self.splash_radius > 0:
            self.area_damage(target, damage, units, buildings, floating_texts)
        else:
            target.take_damage(damage, floating_texts)

        if "수류탄" in self.abilities:
            self.try_throw_grenade(target, now, units, buildings, floating_texts)

        if self.is_suicide:
            self.hp = 0
            
        self.update_direction(
            target.rect.centerx,
            target.rect.centery
        )

    def area_damage(self, target, damage, units, buildings, floating_texts):
        tx = target.rect.centerx
        ty = target.rect.centery

        for unit in units:
            if unit.side != self.side and unit.hp > 0:
                d = math.hypot(unit.rect.centerx - tx, unit.rect.centery - ty)
                if d <= self.splash_radius:
                    unit_type = getattr(unit, "unit_type", TYPE_INFANTRY)
                    final_damage = self.damage_table.get(unit_type, damage)
                    unit.take_damage(final_damage, floating_texts)

        for building in buildings:
            if building.side != self.side and building.hp > 0:
                d = math.hypot(building.rect.centerx - tx, building.rect.centery - ty)
                if d <= self.splash_radius:
                    final_damage = self.damage_table.get(TYPE_BUILDING, damage)
                    building.take_damage(final_damage, floating_texts)
                    
    def try_throw_grenade(self, target, now, units, buildings, floating_texts):
        
        # -----------------------------
        # 현재 수류탄 담당 병사만 사용 가능
        # -----------------------------

        if self.member_index != self.card.get("grenadier_index"):
            return
        
        # 수류탄 쿨타임 확인
        grenade_delay = self.card.get("grenade_delay", 10000)

        if now - self.last_grenade_time < grenade_delay:
            return

        # 수류탄 사거리 확인
        grenade_range = self.card.get("grenade_range", 60)

        if self.distance_to(target) > grenade_range:
            return

        self.last_grenade_time = now

        grenade_damage_table = self.card.get("grenade_damage", {})
        splash_radius = self.card.get("grenade_splash_radius", 45)

        tx = target.rect.centerx
        ty = target.rect.centery

        # 적 유닛에게 광역 피해
        for unit in units:
            if unit.side != self.side and unit.hp > 0:
                d = math.hypot(unit.rect.centerx - tx, unit.rect.centery - ty)

                if d <= splash_radius:
                    unit_type = getattr(unit, "unit_type", TYPE_INFANTRY)
                    damage = grenade_damage_table.get(unit_type, 0)

                    if damage > 0:
                        unit.take_damage(damage, floating_texts)

        # 적 건물에게 광역 피해
        for building in buildings:
            if building.side != self.side and building.hp > 0:
                d = math.hypot(building.rect.centerx - tx, building.rect.centery - ty)

                if d <= splash_radius:
                    damage = grenade_damage_table.get(TYPE_BUILDING, 0)

                    if damage > 0:
                        building.take_damage(damage, floating_texts)

        floating_texts.append(
            FloatingText("수류탄!", self.rect.centerx, self.rect.y - 20, ORANGE)
        )

    def reduce_morale(self, amount):
        if "야마토 정신" in self.abilities:
            return

        self.morale -= amount

        if self.morale <= 0:
            self.morale = 45
            self.suppressed_timer = 120

    def take_damage(self, amount, floating_texts):
        self.hp -= amount

    # 병사 하나가 죽을 정도로 체력이 낮아지면
    # 분대 인원 감소 연출

        if self.hp <= 0:
            self.hp = 0

        floating_texts.append(
            FloatingText(
                f"-{int(amount)}",
                self.rect.centerx,
                self.rect.y,
                WHITE
            )
        )
        
        # -----------------------------
        # 수류탄 담당 병사가 죽으면
        # 다른 병사에게 역할 승계
        # -----------------------------

        if self.hp <= 0:

            if self.is_grenadier:
                self.assign_new_grenadier()
                
    def assign_new_grenadier(self):

        # 이미 다른 병사가 지정됐으면 종료
        if self.card.get("grenadier_index") != self.member_index:
            return

        # 다음 병사 번호 지정
        next_index = self.member_index + 1

        # 분대 인원 범위 안이면 승계
        if next_index < self.card["count"]:

            self.card["grenadier_index"] = next_index

    def distance_to(self, target):
        return math.hypot(
            self.rect.centerx - target.rect.centerx,
            self.rect.centery - target.rect.centery
        )
    
    def prevent_center_building_crossing(self):
        # 중앙 건물 충돌 영역
        center_block = pygame.Rect(410, 220, 180, 220)

        if not self.rect.colliderect(center_block):
            return

        # 왼쪽 라인 유닛은 왼쪽으로 밀어냄
        if self.lane == "left":
            self.x = center_block.left - self.rect.width - 2

        # 오른쪽 라인 유닛은 오른쪽으로 밀어냄
        elif self.lane == "right":
            self.x = center_block.right + 2

        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        
    def move_to_call_in_target(self):
        if self.call_in_target is None:
            self.is_calling_in = False
            return

        tx, ty = self.call_in_target

        dx = tx - self.rect.centerx
        dy = ty - self.rect.centery
        dist = max(1, math.hypot(dx, dy))

        move_speed = max(self.speed, SPEED_NORMAL)

        self.x += dx / dist * move_speed
        self.y += dy / dist * move_speed

        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

        self.animation_state = "move"

        if dist < 6:
            self.is_calling_in = False
            self.call_in_target = None
            
        self.update_direction(tx, ty)
            
            
    def update_direction(self, target_x, target_y):
        dx = target_x - self.rect.centerx
        dy = target_y - self.rect.centery

        # 너무 작은 좌우 차이는 중앙 이동으로 취급
        deadzone = 18

        if abs(dx) <= deadzone and dy < 0:
            self.direction = "up"

        elif abs(dx) <= deadzone and dy > 0:
            self.direction = "down"

        elif dx > deadzone and dy < 0:
            self.direction = "up_right"

        elif dx < -deadzone and dy < 0:
            self.direction = "up_left"

        elif dx > deadzone and dy > 0:
            self.direction = "down_right"

        elif dx < -deadzone and dy > 0:
            self.direction = "down_left"

        elif dx > deadzone:
            self.direction = "right"

        elif dx < -deadzone:
            self.direction = "left"


def create_units_from_card(card_data, x, y, side):
    created = []

    card_data = card_data.copy()

    card_data["squad_max_hp"] = (
        card_data["hp"] *
        card_data["count"]
    )
    # -----------------------------
    # 배치 위치에 따른 콜인 시작 위치
    # 후방 진입로: 맵 아래에서 등장
    # 측면 진입로: 맵 옆에서 등장
    # -----------------------------

    is_rear_spawn = False

    for zone in PLAYER_REAR_ZONES:
        if pygame.Rect(zone).collidepoint(x, y):
            is_rear_spawn = True
            break

    if x < WIDTH // 2:
        card_data["lane"] = "left"
    else:
        card_data["lane"] = "right"

    if is_rear_spawn:
        # 후방 진입로는 아래쪽에서 올라오는 느낌
        spawn_x = x
        spawn_y = HEIGHT + 35
    else:
        # 측면 진입로는 왼쪽/오른쪽 바깥에서 들어오는 느낌
        if x < WIDTH // 2:
            spawn_x = -35
        else:
            spawn_x = WIDTH + 35

        spawn_y = y

    squad_id = get_next_squad_id()

    for i in range(card_data["count"]):
        target_x = x + random.randint(-22, 22)
        target_y = y + random.randint(-18, 18)

        unit = Unit(
            spawn_x + random.randint(-8, 8),
            spawn_y + random.randint(-12, 12),
            side,
            card_data,
            squad_id=squad_id,
            member_index=i
        )

        unit.is_calling_in = True
        unit.call_in_target = (target_x, target_y)

        created.append(unit)

    return created


def create_enemy_infantry():

    data = {
        "name": "미군 일반 보병",
        "icon": "총",
        "cost": 0,
        "unit_type": TYPE_INFANTRY,
        "count": 1,
        "hp": 2500,
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
        "abilities": [],
        "is_ranged_infantry": True,
    }

    # 분대 최대 체력 저장
    data["squad_max_hp"] = (
        data["hp"] *
        data["count"]
    )

    x, y = random.choice(ENEMY_SPAWN_POINTS)

    # 라인 지정
    if x < WIDTH // 2:
        data["lane"] = "left"
    else:
        data["lane"] = "right"

    return Unit(
        x,
        y,
        ENEMY,
        data,
        squad_id=get_next_squad_id()
    )