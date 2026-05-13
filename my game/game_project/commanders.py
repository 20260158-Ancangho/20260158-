# commanders.py
# 지휘관 능력을 관리하는 파일
# 현재는 야마모토 이소로쿠만 구현

from settings import *
from effects import Shell


class YamamotoCommander:
    def __init__(self):
        self.name = "야마모토 이소로쿠"
        self.subtitle = "해군 연합 함대"

    def call_bombardment(self, x, y, shells):
        # 해안 포격
        # 총 4발, 각 포탄마다 조금씩 늦게 떨어짐
        for i in range(BOMBARDMENT_COUNT):
            delay = 45 + i * 35
            shells.append(Shell(x, y, delay))