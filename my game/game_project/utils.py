# utils.py
# 여러 파일에서 공통으로 사용하는 보조 함수들

import math
import pygame
from settings import WHITE

def draw_text(screen, font, text, x, y, color=WHITE):
    img = font.render(text, True, color)
    screen.blit(img, (x, y))

def distance(a, b):
    return math.hypot(
        a.rect.centerx - b.rect.centerx,
        a.rect.centery - b.rect.centery
    )

def clamp(value, low, high):
    return max(low, min(high, value))