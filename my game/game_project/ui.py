# ui.py

import pygame
from settings import *
from utils import draw_text


def draw_select_screen(screen, font, big_font):
    screen.fill((25, 35, 50))

    draw_text(screen, big_font, "지휘관 선택", 390, 80, WHITE)

    card = pygame.Rect(370, 180, 260, 330)
    pygame.draw.rect(screen, DARK, card)
    pygame.draw.rect(screen, WHITE, card, 3)

    draw_text(screen, big_font, "?", 475, 240, WHITE)
    draw_text(screen, font, "야마모토 이소로쿠", 405, 330, WHITE)
    draw_text(screen, font, "해군 연합 함대", 430, 370, YELLOW)

    draw_text(screen, font, "1번: 해안 포격 / 지휘력 3", 385, 420, WHITE)
    draw_text(screen, font, "2번: 해군 배치 / 지휘력 2", 385, 450, WHITE)

    draw_text(screen, font, "클릭해서 선택", 430, 540, ORANGE)


def is_commander_card_clicked(mx, my):
    return 370 <= mx <= 630 and 180 <= my <= 510


def draw_battlefield(screen, font):
    screen.fill((54, 82, 55))

    # -----------------------------
    # 양쪽 도로
    # 중앙은 건물이 있는 구역이므로 길이 아님
    # -----------------------------

    # -----------------------------
    # 중앙 장애물 건물
    # 라인을 간접적으로 분리하는 역할
    # -----------------------------

    center_obstacle = pygame.Rect(410, 220, 180, 220)

    pygame.draw.rect(screen, (55, 65, 55), center_obstacle)
    pygame.draw.rect(screen, (30, 40, 30), center_obstacle, 4)

    draw_text(screen, font, "중앙 건물", 455, 325, GRAY)


def draw_game_ui(
    screen,
    font,
    cost,
    max_cost,
    command_points,
    max_command_points,
    hand,
    next_card,
    selected_card,
    selected_skill
):
    # -----------------------------
    # 왼쪽 지휘력 UI
    # -----------------------------

    pygame.draw.rect(screen, (25, 25, 25), (0, 510, 95, 175))
    pygame.draw.rect(screen, WHITE, (0, 510, 95, 175), 2)

    draw_text(screen, font, "지휘력", 18, 520, YELLOW)
    draw_text(screen, font, f"{command_points}/{max_command_points}", 25, 548, WHITE)

    skill1 = pygame.Rect(15, 585, 65, 35)
    skill2 = pygame.Rect(15, 630, 65, 35)

    pygame.draw.rect(screen, ORANGE if selected_skill == "bombardment" else DARK, skill1)
    pygame.draw.rect(screen, BLUE if selected_skill == "navy" else DARK, skill2)

    pygame.draw.rect(screen, WHITE, skill1, 1)
    pygame.draw.rect(screen, WHITE, skill2, 1)

    draw_text(screen, font, "1 포격", 20, 592, WHITE)
    draw_text(screen, font, "2 해군", 20, 637, WHITE)

    # -----------------------------
    # 다음 카드 UI
    # 카드 UI 왼쪽 위
    # -----------------------------

    pygame.draw.rect(screen, (30, 30, 30), (185, 575, 100, 55))
    pygame.draw.rect(screen, WHITE, (185, 575, 100, 55), 2)

    draw_text(screen, font, "다음", 215, 580, GRAY)

    if next_card:
        draw_text(screen, font, next_card["name"], 193, 605, WHITE)

    # -----------------------------
    # 중앙 아래 코스트 UI
    # -----------------------------

    pygame.draw.rect(screen, (25, 25, 25), (390, 640, 220, 45))
    pygame.draw.rect(screen, WHITE, (390, 640, 220, 45), 2)

    draw_text(screen, font, f"코스트 {cost}/{max_cost}", 445, 652, GREEN)

    # -----------------------------
    # 코스트 바로 위 카드 4장
    # -----------------------------

    keys = ["Q", "W", "E", "R"]
    start_x = 300

    for i, card in enumerate(hand):
        rect = pygame.Rect(start_x + i * 105, 565, 95, 65)

        if selected_card == i:
            pygame.draw.rect(screen, YELLOW, rect)
        else:
            pygame.draw.rect(screen, DARK, rect)

        pygame.draw.rect(screen, WHITE, rect, 2)

        draw_text(screen, font, keys[i], rect.x + 6, rect.y + 4, WHITE)
        draw_text(screen, font, card["name"], rect.x + 7, rect.y + 28, WHITE)
        draw_text(screen, font, f"{card['cost']}", rect.x + 72, rect.y + 4, GREEN)


def draw_placement_preview(screen, selected_card, selected_skill, hand=None):
    mx, my = pygame.mouse.get_pos()

    if selected_card is None and selected_skill is None:
        return

    # 마우스 위치 표시
    pygame.draw.circle(screen, YELLOW, (mx, my), 18, 2)

    # -----------------------------
    # 카드 선택 시 배치 가능 진입로 표시
    # -----------------------------
    if selected_card is not None and hand is not None:
        card = hand[selected_card]

        # 후방 진입로는 기본적으로 배치 가능
        for zone in PLAYER_REAR_ZONES:
            rect = pygame.Rect(zone)
            pygame.draw.rect(screen, (80, 220, 100), rect, 3)

            # 은은한 빛 효과
            glow = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
            glow.fill((80, 220, 100, 45))
            screen.blit(glow, rect.topleft)

        # 측면 진입 가능한 카드만 측면 진입로 표시
        if card.get("can_flank", False):
            for zone in PLAYER_FLANK_ZONES:
                rect = pygame.Rect(zone)
                pygame.draw.rect(screen, (80, 150, 255), rect, 3)

                glow = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
                glow.fill((80, 150, 255, 55))
                screen.blit(glow, rect.topleft)

    # -----------------------------
    # 지휘 스킬 선택 시 배치 가능 지역 표시
    # -----------------------------
    if selected_skill == "navy":
        for zone in PLAYER_REAR_ZONES:
            rect = pygame.Rect(zone)
            pygame.draw.rect(screen, (80, 220, 100), rect, 3)

            glow = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
            glow.fill((80, 220, 100, 45))
            screen.blit(glow, rect.topleft)

        for zone in PLAYER_FLANK_ZONES:
            rect = pygame.Rect(zone)
            pygame.draw.rect(screen, (80, 150, 255), rect, 3)

            glow = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
            glow.fill((80, 150, 255, 55))
            screen.blit(glow, rect.topleft)