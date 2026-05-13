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
    # 중앙 길과 배치 가능 구역 표시
    screen.fill((55, 85, 55))

    # 중앙 건물 기준 길
    pygame.draw.rect(screen, (95, 95, 95), (390, 100, 220, 500))

    # 플레이어 후방 배치 구역
    pygame.draw.rect(screen, (70, 110, 70), PLAYER_REAR_ZONE, 2)

    # 측면 배치 구역
    pygame.draw.rect(screen, (90, 90, 130), PLAYER_LEFT_FLANK_ZONE, 2)
    pygame.draw.rect(screen, (90, 90, 130), PLAYER_RIGHT_FLANK_ZONE, 2)

    draw_text(screen, font, "후방 배치 구역", 430, 620, WHITE)
    draw_text(screen, font, "측면", 105, 230, WHITE)
    draw_text(screen, font, "측면", 815, 230, WHITE)


def draw_game_ui(screen, font, cost, max_cost, command_points, max_command_points, hand, next_card, selected_card, selected_skill):
    pygame.draw.rect(screen, (25, 25, 25), (0, 630, WIDTH, 70))

    draw_text(screen, font, f"코스트: {cost}/{max_cost}", 15, 640, WHITE)
    draw_text(screen, font, f"지휘력: {command_points}/{max_command_points}", 15, 665, YELLOW)

    # 지휘 스킬
    skill1 = pygame.Rect(170, 640, 110, 45)
    skill2 = pygame.Rect(290, 640, 110, 45)

    pygame.draw.rect(screen, ORANGE if selected_skill == "bombardment" else DARK, skill1)
    pygame.draw.rect(screen, BLUE if selected_skill == "navy" else DARK, skill2)

    draw_text(screen, font, "1 포격", 190, 652, WHITE)
    draw_text(screen, font, "2 해군", 310, 652, WHITE)

    # 카드 4장
    keys = ["Q", "W", "E", "R"]
    start_x = 430

    for i, card in enumerate(hand):
        rect = pygame.Rect(start_x + i * 115, 635, 105, 55)

        if selected_card == i:
            pygame.draw.rect(screen, YELLOW, rect)
        else:
            pygame.draw.rect(screen, DARK, rect)

        pygame.draw.rect(screen, WHITE, rect, 2)

        draw_text(screen, font, keys[i], rect.x + 5, rect.y + 5, WHITE)
        draw_text(screen, font, card["name"], rect.x + 8, rect.y + 25, WHITE)
        draw_text(screen, font, f"{card['cost']}C", rect.x + 70, rect.y + 5, GREEN)

    # 다음 카드 표시
    pygame.draw.rect(screen, (45, 45, 45), (900, 635, 85, 55))
    pygame.draw.rect(screen, WHITE, (900, 635, 85, 55), 2)

    draw_text(screen, font, "다음", 920, 638, GRAY)
    if next_card:
        draw_text(screen, font, next_card["name"], 905, 662, WHITE)


def draw_placement_preview(screen, selected_card, selected_skill):
    mx, my = pygame.mouse.get_pos()

    if selected_card is not None or selected_skill is not None:
        pygame.draw.circle(screen, YELLOW, (mx, my), 22, 2)