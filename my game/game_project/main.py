#main.py

import pygame

from settings import *
from ui import draw_select_screen, is_commander_card_clicked
from game_manager import Game


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

                if event.key == pygame.K_1:
                    if game.selected_skill == "bombardment":
                        game.selected_skill = None
                    else:
                        game.selected_skill = "bombardment"

                    game.selected_card = None

                elif event.key == pygame.K_2:
                    if game.selected_skill == "navy":
                        game.selected_skill = None
                    else:
                        game.selected_skill = "navy"

                    game.selected_card = None

                elif event.key == pygame.K_q:
                    if game.selected_card == 0:
                        game.selected_card = None
                    else:
                        game.selected_card = 0

                    game.selected_skill = None

                elif event.key == pygame.K_w:
                    if game.selected_card == 1:
                        game.selected_card = None
                    else:
                        game.selected_card = 1

                    game.selected_skill = None

                elif event.key == pygame.K_e:
                    if game.selected_card == 2:
                        game.selected_card = None
                    else:
                        game.selected_card = 2

                    game.selected_skill = None

                elif event.key == pygame.K_r:
                    if game.selected_card == 3:
                        game.selected_card = None
                    else:
                        game.selected_card = 3

                    game.selected_skill = None

                elif event.key == pygame.K_ESCAPE:
                    game.selected_card = None
                    game.selected_skill = None

            elif event.type == pygame.MOUSEBUTTONDOWN:
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