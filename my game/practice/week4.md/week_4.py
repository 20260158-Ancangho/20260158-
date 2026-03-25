import pygame
import sys
import math
from my_sprites import load_sprite

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sprite Collision: Circle + AABB + OBB")

clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 30)

# 색상
RED = (255, 0, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)

# 크기
RECT_SIZE = 80
GAP = RECT_SIZE * 3

# 스케일 함수
def fit_surface(surf, box_size):
    w, h = surf.get_size()
    scale = min(box_size / w, box_size / h)
    new_size = (int(w * scale), int(h * scale))
    return pygame.transform.scale(surf, new_size)

# 스프라이트 로드
player_img = fit_surface(load_sprite("adventurer"), RECT_SIZE)
stone_img_orig  = fit_surface(load_sprite("stone"), RECT_SIZE)

# 중앙 오브젝트 (회전)
center_rect = pygame.Rect(
    WIDTH // 2 - RECT_SIZE // 2,
    HEIGHT // 2 - RECT_SIZE // 2,
    RECT_SIZE,
    RECT_SIZE
)

# 플레이어
player_rect = pygame.Rect(
    center_rect.x - GAP,
    center_rect.y,
    RECT_SIZE,
    RECT_SIZE
)

speed = 5
angle = 0
rotation_speed = 0.5

# ---------------------------
# SAT OBB 충돌 함수
# ---------------------------
def sat_collision(corners1, corners2):
    def get_axes(corners):
        axes = []
        for i in range(len(corners)):
            p1 = corners[i]
            p2 = corners[(i+1)%len(corners)]
            edge = (p2[0]-p1[0], p2[1]-p1[1])
            normal = (-edge[1], edge[0])
            length = math.hypot(*normal)
            if length != 0:
                normal = (normal[0]/length, normal[1]/length)
            axes.append(normal)
        return axes

    def project(corners, axis):
        dots = [c[0]*axis[0] + c[1]*axis[1] for c in corners]
        return min(dots), max(dots)

    axes = get_axes(corners1) + get_axes(corners2)
    for axis in axes:
        min1, max1 = project(corners1, axis)
        min2, max2 = project(corners2, axis)
        if max1 < min2 or max2 < min1:
            return False
    return True

# ---------------------------
# OBB 꼭짓점 계산
# ---------------------------
def get_obb_points(rect, angle_deg):
    w, h = rect.width, rect.height
    rad = math.radians(-angle_deg)
    cos_a = math.cos(rad)
    sin_a = math.sin(rad)
    cx, cy = rect.center
    corners = [(-w/2,-h/2), (w/2,-h/2), (w/2,h/2), (-w/2,h/2)]
    points = []
    for x, y in corners:
        rx = x*cos_a - y*sin_a + cx
        ry = x*sin_a + y*cos_a + cy
        points.append((rx, ry))
    return points

# ---------------------------
# 메인 루프
# ---------------------------
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player_rect.x -= speed
    if keys[pygame.K_RIGHT]:
        player_rect.x += speed
    if keys[pygame.K_UP]:
        player_rect.y -= speed
    if keys[pygame.K_DOWN]:
        player_rect.y += speed

    # 회전 속도
    current_rotation_speed = rotation_speed * 5 if keys[pygame.K_z] else rotation_speed
    angle += current_rotation_speed
    angle %= 360

    # 회전 이미지
    stone_img = pygame.transform.rotate(stone_img_orig, angle)
    stone_rect = stone_img.get_rect(center=center_rect.center)

    # 중심 좌표
    player_center = player_rect.center
    center_center = center_rect.center

    radius = RECT_SIZE // 2

    # ---------------------------
    # 충돌 검사
    # ---------------------------
    # 1️⃣ Circle 충돌
    dx = player_center[0] - center_center[0]
    dy = player_center[1] - center_center[1]
    distance_sq = dx*dx + dy*dy
    circle_collision = distance_sq < (radius * 2) ** 2

    # 2️⃣ AABB 충돌
    aabb_collision = player_rect.colliderect(center_rect)

    # 3️⃣ OBB 충돌
    player_corners = get_obb_points(player_rect, 0)
    stone_corners = get_obb_points(center_rect, angle)
    obb_collision = sat_collision(player_corners, stone_corners)

    # ---------------------------
    # 배경색
    # ---------------------------
    if circle_collision or aabb_collision or obb_collision:
        screen.fill(YELLOW)
    else:
        screen.fill(WHITE)

    # ---------------------------
    # 스프라이트 출력
    # ---------------------------
    pw, ph = player_img.get_size()
    screen.blit(player_img, (player_rect.centerx - pw//2, player_rect.centery - ph//2))
    screen.blit(stone_img, stone_rect.topleft)

    # ---------------------------
    # 충돌 박스 시각화
    # ---------------------------
    # 🔴 AABB
    pygame.draw.rect(screen, RED, center_rect, 2)
    pygame.draw.rect(screen, RED, player_rect, 2)

    # 🔵 Circle
    pygame.draw.circle(screen, BLUE, center_center, radius, 2)
    pygame.draw.circle(screen, BLUE, player_center, radius, 2)

    # 🟢 OBB
    pygame.draw.polygon(screen, GREEN, stone_corners, 2)
    pygame.draw.polygon(screen, GREEN, player_corners, 2)

    # ---------------------------
    # 충돌 텍스트
    # ---------------------------
    texts = []
    if circle_collision:
        texts.append("Circle: HIT")
    else:
        texts.append("Circle: ---")

    if aabb_collision:
        texts.append("AABB: HIT")
    else:
        texts.append("AABB: ---")

    if obb_collision:
        texts.append("OBB: HIT")
    else:
        texts.append("OBB: ---")

    for i, t in enumerate(texts):
        surf = font.render(t, True, (0,0,0))
        screen.blit(surf, (10, 10 + i*30))

    pygame.display.flip()
    clock.tick(60)