import pygame
import sys
import math
import random

pygame.init()

# 화면 설정
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Just Game")

# 폰트
font = pygame.font.SysFont(None, 30)
big_font = pygame.font.SysFont(None, 60)

# 색상
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

# 플레이어
x, y = WIDTH // 2, HEIGHT // 2
size = 40
speed = 10

# 동그라미
circle_radius = 10
circle_count = 5

def spawn_circles():
    return [
        (
            random.randint(circle_radius, WIDTH - circle_radius),
            random.randint(circle_radius, HEIGHT - circle_radius)
        )
        for _ in range(circle_count)
    ]

circles = spawn_circles()

# 점수
score = 0

# 시간
last_eat_time = pygame.time.get_ticks()

# 게임 상태
game_over = False

clock = pygame.time.Clock()

# 버튼
button_rect = pygame.Rect(WIDTH//2 - 80, HEIGHT//2 + 40, 160, 50)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if game_over and event.type == pygame.MOUSEBUTTONDOWN:
            if button_rect.collidepoint(event.pos):
                # 리셋
                x, y = WIDTH // 2, HEIGHT // 2
                circles = spawn_circles()
                score = 0
                last_eat_time = pygame.time.get_ticks()
                game_over = False

    if not game_over:
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0

        if keys[pygame.K_LEFT]:
            dx -= speed
        if keys[pygame.K_RIGHT]:
            dx += speed
        if keys[pygame.K_UP]:
            dy -= speed
        if keys[pygame.K_DOWN]:
            dy += speed

        # 대각선 보정
        if dx != 0 and dy != 0:
            dx /= math.sqrt(2)
            dy /= math.sqrt(2)

        x += dx
        y += dy

        # 화면 제한
        x = max(0, min(WIDTH - size, x))
        y = max(0, min(HEIGHT - size, y))

        # 충돌 체크
        player_center = (x + size//2, y + size//2)
        new_circles = []

        for cx, cy in circles:
            dist = math.hypot(player_center[0] - cx, player_center[1] - cy)

            if dist < circle_radius + size//2:
                score += 1
                last_eat_time = pygame.time.get_ticks()
            else:
                new_circles.append((cx, cy))

        circles = new_circles

        # 다 먹으면 재생성
        if not circles:
            circles = spawn_circles()

        # ⏱️ 시간 계산
        current_time = pygame.time.get_ticks()
        remaining_time = max(0, 5 - (current_time - last_eat_time) / 1000)

        # 게임 오버 체크
        if remaining_time <= 0:
            game_over = True

    # 🎨 그리기
    screen.fill(WHITE)

    # 플레이어
    pygame.draw.rect(screen, BLUE, (x, y, size, size))

    # 동그라미
    for cx, cy in circles:
        pygame.draw.circle(screen, RED, (cx, cy), circle_radius)

    # 점수 UI
    score_text = font.render(f"Score: {score}", True, BLACK)
    screen.blit(score_text, (WIDTH - 140, 10))

    # ⏱️ 시간 UI (색상 변경 포함)
    time_color = RED if not game_over and remaining_time < 3 else BLACK
    time_text = font.render(f"Time: {remaining_time:.1f}", True, time_color)
    screen.blit(time_text, (WIDTH - 140, 40))

    # FPS
    fps = int(clock.get_fps())
    fps_text = font.render(f"FPS: {fps}", True, BLACK)
    screen.blit(fps_text, (10, 10))

    # 게임 오버 화면
    if game_over:
        # GAME OVER 텍스트
        over_text = big_font.render("GAME OVER", True, RED)
        over_rect = over_text.get_rect(center=(WIDTH//2, HEIGHT//2 - 40))
        screen.blit(over_text, over_rect)
        # Retry 버튼
        button_rect = pygame.Rect(0, 0, 160, 50)
        button_rect.center = (WIDTH//2, HEIGHT//2 + 40)
        pygame.draw.rect(screen, BLACK, button_rect)
        
        retry_text = font.render("Retry", True, WHITE)
        retry_rect = retry_text.get_rect(center=button_rect.center)
        screen.blit(retry_text, retry_rect)

    pygame.display.flip()
    clock.tick(60)