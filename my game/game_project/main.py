# main.py

import pygame

from settings import *
from ui import draw_select_screen, is_commander_card_clicked
from game import Game


pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("WW2 RTS Prototype - Card System")

clock = pygame.time.Clock()

font = pygame.font.SysFont("malgungothic", 18)
big_font = pygame.font.SysFont("malgungothic", 42)

game_state = STATE_SELECT
game = None

running = True

while running:
    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if game_state == STATE_SELECT:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()

                if is_commander_card_clicked(mx, my):
                    game = Game()
                    game_state = STATE_GAME

        elif game_state == STATE_GAME:
            if event.type == pygame.KEYDOWN:
                # 지휘 스킬 선택
                if event.key == pygame.K_1:
                    game.select_skill("bombardment")

                elif event.key == pygame.K_2:
                    game.select_skill("navy")

                # 카드 선택
                elif event.key == pygame.K_q:
                    game.select_card(0)

                elif event.key == pygame.K_w:
                    game.select_card(1)

                elif event.key == pygame.K_e:
                    game.select_card(2)

                elif event.key == pygame.K_r:
                    game.select_card(3)

                # 선택 취소
                elif event.key == pygame.K_ESCAPE:
                    game.selected_card = None
                    game.selected_skill = None

            if event.type == pygame.MOUSEBUTTONDOWN:
                # 좌클릭으로 선택한 카드/스킬 배치
                if event.button == 1:
                    mx, my = pygame.mouse.get_pos()
                    game.place_selected(mx, my)

    if game_state == STATE_SELECT:
        draw_select_screen(screen, font, big_font)

    elif game_state == STATE_GAME:
        game.update()
        game.draw(screen, font)

    pygame.display.flip()

pygame.quit()