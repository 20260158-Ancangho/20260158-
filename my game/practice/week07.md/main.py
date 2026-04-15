import pygame, sys, random, os
pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

WHITE=(255,255,255)
GRAY=(40,40,40)
RED=(220,50,50)
YELLOW=(240,200,0)
ORANGE=(240,140,0)
GREEN=(50,200,50)

font = pygame.font.SysFont("malgungothic", 28)

BASE_DIR = os.path.dirname(__file__)
ASSET_DIR = os.path.join(BASE_DIR, "assets")

brick_img = pygame.image.load(os.path.join(ASSET_DIR, "brick.png")).convert()

# 🔥 흰색 제거
brick_img.set_colorkey((255,255,255))

pygame.mixer.music.load(os.path.join(ASSET_DIR, "bgm.mp3"))
hit_sound = pygame.mixer.Sound(os.path.join(ASSET_DIR, "jump.wav"))
pygame.mixer.music.play(-1)

# ======================
# 🔥 자동 크롭
# ======================
def crop_surface(surf):
    rect = surf.get_bounding_rect()
    return surf.subsurface(rect)

# ======================
# 🔥 핵심: "왼쪽 단일 타일만 사용"
# ======================
# (이미지 구조 기준으로 가장 안전한 범위)
brick_sprites = [
    brick_img.subsurface((0,   0, 120, 150)),  # 회색
    brick_img.subsurface((0, 150, 120, 150)),  # 빨강
    brick_img.subsurface((0, 300, 120, 150)),  # 은색
    brick_img.subsurface((0, 450, 120, 150)),  # 갈색
]

sprites = [
    pygame.transform.scale(s, (72,22))
    for s in brick_sprites
]

# ======================
PAD = pygame.Rect(350,560,100,12)
BALL = pygame.Rect(0,0,16,16)

particles=[]

def spawn_particles(x,y):
    for _ in range(10):
        particles.append({
            "x":x,"y":y,
            "vx":random.uniform(-3,3),
            "vy":random.uniform(-4,-1),
            "life":30
        })

def update_particles():
    for p in particles[:]:
        p["x"]+=p["vx"]
        p["y"]+=p["vy"]
        p["vy"]+=0.2
        p["life"]-=1
        if p["life"]<=0:
            particles.remove(p)
            
def crop_surface(surf):
    rect = surf.get_bounding_rect()
    return surf.subsurface(rect)

brick_sprites = [crop_surface(s) for s in brick_sprites]

def draw_particles():
    for p in particles:
        pygame.draw.circle(screen,YELLOW,(int(p["x"]),int(p["y"])),2)

def draw_bar(x,y,w,h,ratio,color):
    pygame.draw.rect(screen,(80,80,80),(x,y,w,h))
    pygame.draw.rect(screen,color,(x,y,w*ratio,h))

def make_blocks(rows):
    blocks=[]
    for r in range(rows):
        for c in range(10):
            rect = pygame.Rect(5+c*77,60+r*27,72,22)
            blocks.append({"rect":rect,"sprite":sprites[r%4]})
    return blocks

def reset_ball():
    BALL.centerx = PAD.centerx
    BALL.bottom = PAD.top

def game_over():
    while True:
        screen.fill(GRAY)
        screen.blit(font.render("GAME OVER",True,RED),(300,250))
        screen.blit(font.render("R: Retry / SPACE: Quit",True,WHITE),(240,320))
        pygame.display.flip()
        for e in pygame.event.get():
            if e.type==pygame.QUIT: sys.exit()
            if e.type==pygame.KEYDOWN:
                if e.key==pygame.K_r: return "retry"
                if e.key==pygame.K_SPACE: sys.exit()

def main():
    boss_idx=0
    lives=3
    blocks=make_blocks(3)
    boss_stage=False

    BOSSES=[
        {"hp":3,"pattern":"basic","color":WHITE},
        {"hp":3,"pattern":"cylinder","color":ORANGE},
        {"hp":5,"pattern":"fan","color":RED}
    ]

    bx,by=300,-300
    launched=False
    attack_timer=0
    phase_timer=0
    boss_phase="attack"

    while True:
        dt=clock.tick(60)/1000
        keys=pygame.key.get_pressed()
        speed_scale=1.75 if keys[pygame.K_LSHIFT] else 1

        for e in pygame.event.get():
            if e.type==pygame.QUIT: sys.exit()
            if e.type==pygame.KEYDOWN:
                if e.key==pygame.K_SPACE:
                    if not boss_stage or boss_phase=="player":
                        launched=True

        if keys[pygame.K_LEFT]: PAD.x-=500*dt*speed_scale
        if keys[pygame.K_RIGHT]: PAD.x+=500*dt*speed_scale
        PAD.x=max(0,min(WIDTH-PAD.width,PAD.x))

        # ======================
        # 벽돌
        # ======================
        if not boss_stage:

            if not launched:
                reset_ball()
            else:
                BALL.x+=bx*dt*speed_scale
                BALL.y+=by*dt*speed_scale

                if BALL.left<=0: BALL.left=0; bx=abs(bx)
                if BALL.right>=WIDTH: BALL.right=WIDTH; bx=-abs(bx)
                if BALL.top<=0: BALL.top=0; by=abs(by)

                if BALL.colliderect(PAD) and by>0:
                    hit_sound.play()
                    BALL.bottom=PAD.top
                    by=-abs(by)

                for b in blocks[:]:
                    if BALL.colliderect(b["rect"]):
                        spawn_particles(b["rect"].centerx,b["rect"].centery)
                        blocks.remove(b)
                        by=-by
                        break

                if BALL.bottom>=HEIGHT:
                    lives-=1
                    launched=False
                    if lives<=0:
                        if game_over()=="retry":
                            return main()

            if not blocks:
                boss_stage=True
                boss=BOSSES[boss_idx].copy()
                boss["max_hp"]=boss["hp"]
                boss["rect"]=pygame.Rect(340,80,120,40)
                boss["projectiles"]=[]
                launched=False
                BALL.y=-100
                attack_timer=0
                phase_timer=0
                boss_phase="attack"

        # ======================
        # 보스
        # ======================
        else:
            phase_timer+=dt
            attack_timer+=dt

            if boss_phase=="attack":
                if attack_timer>=0.6:
                    attack_timer=0
                    for _ in range(3):
                        x=random.randint(0,WIDTH-16)
                        boss["projectiles"].append({
                            "rect":pygame.Rect(x,0,16,16),
                            "vel":[0,300]
                        })

                for p in boss["projectiles"][:]:
                    p["rect"].y+=p["vel"][1]*dt
                    if PAD.colliderect(p["rect"]):
                        lives-=1
                        boss["projectiles"].remove(p)
                    if p["rect"].top>HEIGHT:
                        boss["projectiles"].remove(p)

                if phase_timer>=15:
                    boss_phase="player"
                    phase_timer=0
                    boss["projectiles"].clear()
                    launched=False

            else:
                if not launched:
                    reset_ball()
                else:
                    BALL.x+=bx*dt
                    BALL.y+=by*dt

                    if BALL.left<=0: BALL.left=0; bx=abs(bx)
                    if BALL.right>=WIDTH: BALL.right=WIDTH; bx=-abs(bx)
                    if BALL.top<=0: BALL.top=0; by=abs(by)

                    if BALL.colliderect(PAD) and by>0:
                        hit_sound.play()
                        BALL.bottom=PAD.top
                        by=-abs(by)

                    if BALL.colliderect(boss["rect"]):
                        boss["hp"]-=1
                        launched=False
                        BALL.y=-100
                        boss_phase="attack"
                        phase_timer=0

        update_particles()

        screen.fill(GRAY)
        pygame.draw.rect(screen,WHITE,PAD)
        pygame.draw.ellipse(screen,WHITE,BALL)

        if not boss_stage:
            for b in blocks:
                screen.blit(b["sprite"],b["rect"])
        else:
            pygame.draw.rect(screen,boss["color"],boss["rect"])
            draw_bar(250,20,300,20,boss["hp"]/boss["max_hp"],RED)

        draw_particles()
        draw_bar(20,20,200,20,lives/3,GREEN)

        if not launched and (not boss_stage or boss_phase=="player"):
            screen.blit(font.render("SPACE TO LAUNCH",True,YELLOW),(260,300))

        pygame.display.flip()
print(brick_img.get_size())

main()