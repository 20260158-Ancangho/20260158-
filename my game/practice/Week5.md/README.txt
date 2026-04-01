import pygame
import sys
import random

pygame.init()

# --- 기본 설정 ---
WIDTH, HEIGHT = 800, 600
FPS = 60

WHITE = (255, 255, 255)
GRAY = (40, 40, 40)
RED = (220, 50, 50)
YELLOW = (240, 200, 0)
ORANGE = (240, 140, 0)
BLUE = (50, 120, 220)
GREEN = (50, 200, 50)

BLOCK_COLORS = [RED, ORANGE, YELLOW, GREEN, BLUE]

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Breakout Boss Edition")
clock = pygame.time.Clock()

def get_korean_font(size):
    candidates = ["malgungothic","applegothic","nanumgothic","notosanscjk"]
    for name in candidates:
        font = pygame.font.SysFont(name, size)
        if font.get_ascent()>0:
            return font
    return pygame.font.SysFont(None, size)

font = get_korean_font(36)
font_big = get_korean_font(72)

# --- 레벨 ---
LEVELS = [
    {"rows": 3, "ball_speed": 5, "label": "Lv.1"},
    {"rows": 5, "ball_speed": 6, "label": "Lv.2"},
    {"rows": 7, "ball_speed": 8, "label": "Lv.3"},
]

PAD_W, PAD_H = 100, 12
BALL_R = 8
BLOCK_W, BLOCK_H = 72, 22
BLOCK_COLS = 10
BLOCK_MARGIN = 5
BLOCK_TOP = 60

PAD_SPEED = 700

# 보스 설정
BOSSES = [
    {"color": WHITE,  "hp": 3, "pattern": "basic"},
    {"color": ORANGE, "hp": 3, "pattern": "cylinder"},
    {"color": RED,    "hp": 3, "pattern": "fast_multi"},
]

# --- 함수 ---
def make_blocks(rows):
    blocks=[]
    for r in range(rows):
        for c in range(BLOCK_COLS):
            x = BLOCK_MARGIN + c*(BLOCK_W+BLOCK_MARGIN)
            y = BLOCK_TOP + r*(BLOCK_H+BLOCK_MARGIN)
            color = BLOCK_COLORS[r%len(BLOCK_COLORS)]
            blocks.append({"rect":pygame.Rect(x,y,BLOCK_W,BLOCK_H),"color":color,"hp":1})
    return blocks

def draw_hud(score, lives, level_cfg):
    screen.blit(font.render(f"Score: {score}",True,WHITE),(10,10))
    screen.blit(font.render(f"Lives: {'♥ '*lives}",True,RED),(WIDTH-180,10))
    screen.blit(font.render(level_cfg["label"],True,YELLOW),(WIDTH//2-25,10))

def draw_boss_hud(boss):
    screen.blit(font.render(f"Boss HP: {'♥ '*boss['hp']}",True,RED),(10,50))

def message_screen(title, color, score):
    screen.fill(GRAY)
    screen.blit(font_big.render(title,True,color),(WIDTH//2-240,220))
    screen.blit(font.render(f"Score: {score}",True,WHITE),(350,310))
    screen.blit(font.render("R: Restart   Q: Quit",True,WHITE),(270,360))
    pygame.display.flip()
    while True:
        for e in pygame.event.get():
            if e.type==pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type==pygame.KEYDOWN:
                if e.key==pygame.K_r:
                    return True
                if e.key==pygame.K_q:
                    pygame.quit()
                    sys.exit()

def reset_ball_on_pad(ball,pad):
    ball.centerx = pad.centerx
    ball.bottom  = pad.top-2
    return [float(ball.x), float(ball.y)]

# --- 메인 ---
def main():
    score=0
    lives=3
    level_idx=0
    boss_idx=0

    pad = pygame.Rect(WIDTH//2-PAD_W//2, HEIGHT-40, PAD_W, PAD_H)
    ball = pygame.Rect(0,0,BALL_R*2,BALL_R*2)
    ball_pos = reset_ball_on_pad(ball,pad)
    launched=False

    blocks = make_blocks(LEVELS[level_idx]["rows"])
    bx = LEVELS[level_idx]["ball_speed"]
    by = -LEVELS[level_idx]["ball_speed"]

    boss_stage=False
    boss=None
    boss_timer=0
    player_phase=False

    while True:
        dt = clock.tick(FPS)/1000

        # 입력
        for e in pygame.event.get():
            if e.type==pygame.QUIT:
                pygame.quit()
                sys.exit()
            if e.type==pygame.KEYDOWN and e.key==pygame.K_SPACE:
                if boss_stage and player_phase and not launched:
                    launched=True
                if not boss_stage and not launched:
                    launched=True

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and pad.left>0:
            pad.x -= PAD_SPEED*dt
        if keys[pygame.K_RIGHT] and pad.right<WIDTH:
            pad.x += PAD_SPEED*dt

        # --- 일반 플레이 ---
        if not boss_stage:
            if not launched:
                ball_pos = reset_ball_on_pad(ball,pad)
            else:
                ball_pos[0]+=bx
                ball_pos[1]+=by
                ball.x=int(ball_pos[0])
                ball.y=int(ball_pos[1])

                # 벽 충돌
                if ball.left<=0 or ball.right>=WIDTH: bx=-bx
                if ball.top<=0: by=-by

                # 패들 충돌
                if ball.colliderect(pad) and by>0:
                    offset=(ball.centerx-pad.centerx)/(PAD_W/2)
                    bx=offset*LEVELS[level_idx]["ball_speed"]
                    by=-abs(by)

                # 블록 충돌
                hit=None
                for b in blocks:
                    if ball.colliderect(b["rect"]):
                        hit=b
                        break
                if hit:
                    blocks.remove(hit)
                    score+=10
                    by=-by

                # 바닥
                if ball.bottom>=HEIGHT:
                    lives-=1
                    launched=False
                    ball_pos=reset_ball_on_pad(ball,pad)
                    if lives<=0:
                        if message_screen("GAME OVER",RED,score):
                            main()
                        return

            # 레벨 클리어 → 보스전
            if not blocks:
                boss_stage=True
                boss = BOSSES[boss_idx].copy()
                boss["projectiles"]=[]
                boss_timer=0
                player_phase=False
                launched=False
                ball_pos=None

            # 렌더링
            screen.fill(GRAY)
            for b in blocks:
                pygame.draw.rect(screen,b["color"],b["rect"])
            pygame.draw.rect(screen,WHITE,pad)
            pygame.draw.ellipse(screen,WHITE,ball)
            draw_hud(score,lives,LEVELS[level_idx])
            pygame.display.flip()

        # --- 보스 스테이지 ---
        else:
            # 보스 공격 Phase
            if not player_phase:
                boss_timer+=dt

                # 보스 공격 생성
                if boss_timer>=1.0:
                    boss_timer=0
                    if boss["pattern"]=="basic":
                        r = BALL_R*1.5
                        x = random.randint(0,WIDTH-int(r*2))
                        boss["projectiles"].append({
                            "rect":pygame.Rect(x,-r*2,int(r*2),int(r*2)),
                            "vel":[0,5],
                            "shape":"circle"
                        })
                    elif boss["pattern"]=="cylinder":
                        w,h=24,48
                        x = random.randint(0,WIDTH-w)
                        boss["projectiles"].append({
                            "rect":pygame.Rect(x,-h,w,h),
                            "vel":[0,8],
                            "shape":"rect","warn":True,"warn_time":0.7
                        })
                    elif boss["pattern"]=="fast_multi":
                        r = BALL_R*2
                        x = random.randint(0,WIDTH-int(r*2))
                        boss["projectiles"].append({
                            "rect":pygame.Rect(x,-r*2,int(r*2),int(r*2)),
                            "vel":[random.uniform(-3,3),6],
                            "shape":"circle"
                        })

                # 업데이트 공격들
                for p in boss["projectiles"][:]:
                    if p.get("shape")=="rect" and p.get("warn",False):
                        p["warn_time"]-=dt
                        if p["warn_time"]<=0:
                            p["warn"]=False
                    else:
                        p["rect"].y+=p["vel"][1]
                        p["rect"].x+=p["vel"][0]

                    if pad.colliderect(p["rect"]):
                        lives-=1
                        boss["projectiles"].remove(p)
                        if lives<=0:
                            if message_screen("GAME OVER",RED,score):
                                main()
                            return

                    if p["rect"].top>HEIGHT:
                        boss["projectiles"].remove(p)

                # 15초가 지나면 플레이어 턴 시작
                if boss_timer>=15:
                    boss["projectiles"].clear()
                    player_phase=True
                    launched=False
                    ball_pos=reset_ball_on_pad(ball,pad)

                # 렌더링 보스 공격
                screen.fill(GRAY)
                pygame.draw.rect(screen,WHITE,pad)
                pygame.draw.rect(screen,boss["color"],pygame.Rect(boss["rect"]))
                for p in boss["projectiles"]:
                    if p["shape"]=="circle":
                        pygame.draw.ellipse(screen,RED,p["rect"])
                    else:
                        if p.get("warn",False):
                            pygame.draw.rect(screen,YELLOW,p["rect"])
                        else:
                            pygame.draw.rect(screen,ORANGE,p["rect"])
                draw_boss_hud(boss)
                pygame.display.flip()

            # --- 플레이어 Phase ---
            else:
                # 플레이어 발사 준비
                if not launched:
                    screen.fill(GRAY)
                    pygame.draw.rect(screen,WHITE,pad)
                    draw_boss_hud(boss)
                    text = font.render("SPACE to launch",True,YELLOW)
                    screen.blit(text,(WIDTH//2 - text.get_width()//2,HEIGHT//2+40))
                    pygame.display.flip()
                    continue

                # 플레이어 공 이동
                ball_pos[0]+=bx
                ball_pos[1]+=by
                ball.x=int(ball_pos[0])
                ball.y=int(ball_pos[1])

                if ball.left<=0 or ball.right>=WIDTH: bx=-bx
                if ball.top<=0: by=-by
                if ball.colliderect(pad) and by>0: by=-abs(by)

                # 보스 맞음
                if ball.colliderect(pygame.Rect(boss["rect"])):
                    boss["hp"]-=1
                    launched=False
                    ball_pos=None
                    player_phase=False
                    boss_timer=0
                    boss["projectiles"].clear()
                    if boss["hp"]<=0:
                        boss_stage=False
                        boss_idx+=1
                        level_idx+=1
                        if level_idx>=len(LEVELS):
                            if message_screen("GAME CLEAR!",YELLOW,score):
                                return
                        else:
                            blocks=make_blocks(LEVELS[level_idx]["rows"])
                            bx=LEVELS[level_idx]["ball_speed"]
                            by=-LEVELS[level_idx]["ball_speed」

                # 바닥
                if ball.bottom>=HEIGHT:
                    launched=False
                    ball_pos=None
                    player_phase=False
                    boss_timer=0
                    boss["projectiles"].clear()

                # 렌더링 플레이어공
                screen.fill(GRAY)
                pygame.draw.rect(screen,WHITE,pad)
                pygame.draw.rect(screen,boss["color"],pygame.Rect(boss["rect"]))
                pygame.draw.ellipse(screen,WHITE,ball)
                draw_boss_hud(boss)
                pygame.display.flip()

main()
