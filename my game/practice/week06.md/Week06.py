import pygame, sys, random
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

font = pygame.font.SysFont("malgungothic", 28)

# 사운드
pygame.mixer.music.load(".:\week06.md\bgm.mp3")
pygame.mixer.music.play(-1)
hit_sound = pygame.mixer.Sound(".:\week06.md\jump.wav")

PAD = pygame.Rect(350,560,100,12)
BALL = pygame.Rect(0,0,16,16)

def main():
    boss_idx=0

    BOSSES=[
        {"hp":3,"pattern":"basic"},
        {"hp":3,"pattern":"cylinder_mix"},
        {"hp":5,"pattern":"move_attack"}
    ]

    boss=BOSSES[boss_idx].copy()
    boss["rect"]=pygame.Rect(340,80,120,40)
    boss["projectiles"]=[]
    boss["vx"]=200

    bx,by=5,-5
    launched=False

    attack_timer=0
    phase_timer=0

    while True:
        dt=clock.tick(60)/1000

        for e in pygame.event.get():
            if e.type==pygame.QUIT: sys.exit()
            if e.type==pygame.KEYDOWN and e.key==pygame.K_SPACE:
                launched=True

        keys=pygame.key.get_pressed()
        if keys[pygame.K_LEFT]: PAD.x-=500*dt
        if keys[pygame.K_RIGHT]: PAD.x+=500*dt

        # ======================
        # 🔴 보스 이동 (3번 전용)
        # ======================
        if boss["pattern"]=="move_attack":
            boss["rect"].x += boss["vx"]*dt
            if boss["rect"].left<=0 or boss["rect"].right>=WIDTH:
                boss["vx"]*=-1

        attack_timer+=dt

        # ======================
        # 🔴 공격 생성
        # ======================
        if attack_timer>=1:
            attack_timer=0

            # 🔵 기본 탄막 (모든 보스 공통)
            r=16
            x=random.randint(0,WIDTH-r)
            boss["projectiles"].append({
                "rect":pygame.Rect(x,-r,r,r),
                "vel":[random.uniform(-2,2),5],
                "type":"bullet"
            })

            # 🟠 2번 보스 추가 패턴
            if boss["pattern"]=="cylinder_mix":
                w,h=30,60
                x=random.randint(0,WIDTH-w)
                boss["projectiles"].append({
                    "rect":pygame.Rect(x,-h,w,h),
                    "vel":[0,15],
                    "type":"cylinder",
                    "warn":True,
                    "timer":1.0
                })

        # ======================
        # 🔴 투사체 처리
        # ======================
        for p in boss["projectiles"][:]:
            if p.get("warn"):
                p["timer"]-=dt
                if p["timer"]<=0:
                    p["warn"]=False
            else:
                p["rect"].x+=p["vel"][0]
                p["rect"].y+=p["vel"][1]

            if PAD.colliderect(p["rect"]):
                boss["projectiles"].remove(p)

            if p["rect"].top>HEIGHT:
                boss["projectiles"].remove(p)

        # ======================
        # 🔵 공 로직
        # ======================
        if not launched:
            BALL.centerx=PAD.centerx
            BALL.bottom=PAD.top
        else:
            BALL.x+=bx
            BALL.y+=by

            if BALL.left<=0 or BALL.right>=WIDTH: bx=-bx
            if BALL.top<=0: by=-by

            if BALL.colliderect(PAD) and by>0:
                hit_sound.play()
                by=-abs(by)

            if BALL.colliderect(boss["rect"]):
                boss["hp"]-=1
                launched=False

        # ======================
        # 렌더링
        # ======================
        screen.fill(GRAY)

        pygame.draw.rect(screen,WHITE,PAD)
        pygame.draw.rect(screen,ORANGE,boss["rect"])
        pygame.draw.ellipse(screen,WHITE,BALL)

        # 🔴 보스 체력 표시 (항상 출력)
        screen.blit(font.render(f"Boss HP: {'♥ '*boss['hp']}",True,RED),(10,50))

        # 투사체
        for p in boss["projectiles"]:
            if p.get("warn"):
                pygame.draw.rect(screen,YELLOW,p["rect"])
            elif p["type"]=="cylinder":
                pygame.draw.rect(screen,ORANGE,p["rect"])
            else:
                pygame.draw.ellipse(screen,RED,p["rect"])

        pygame.display.flip()

main()