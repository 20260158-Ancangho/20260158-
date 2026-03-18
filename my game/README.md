20260158-안창호

Week 3 실습 기록

목표
플레이어 캐릭터를 키보드로 움직일 수 있게 구현하고,  
점수 시스템, 동그라미 먹기, Game Over UI, 다시하기 버튼까지 포함한 간단한 미니게임 완성

AI 대화 기록

**Q1: Pygame에서 키보드 입력을 받는 방법은?**

- AI 답변: `pygame.key.get_pressed()` 사용
- 적용 결과: 성공, 방향키 입력 감지 가능

**Q2: 대각선 이동 속도가 너무 빠른데 어떻게 보정하지?**

- AI 답변: 피타고라스 정리 이용, dx와 dy를 √2로 나눠 속도 조정
- 시행착오: 처음에는 단순 더하기만 사용 → 대각선이 빠름
- 최종 해결: `if dx != 0 and dy != 0: dx/=math.sqrt(2); dy/=math.sqrt(2)` 적용헀다.

**Q3: 화면 밖으로 이동 못하게 제한하고 싶어.**

- AI 답변: `x = max(0, min(WIDTH-size, x))` / `y = max(0, min(HEIGHT-size, y))` 사용.
- 적용 결과: 플레이어가 화면 밖으로 못 나감.

**Q4: 점수 시스템과 Game Over 조건을 어떻게 만들 수 있어?**

- AI 답변: 
  - 동그라미 충돌 시 `score += 1`  
  - 마지막으로 먹은 시간 저장 → 10초 이상 지나면 Game Over  
  - Game Over 화면 + Retry 버튼 구현.
- 적용 결과: 점수 UI, 시간 UI, Game Over, Retry 모두 정상 작동.

**Q5: Game Over UI를 중앙에 정렬하고 싶어요.**

- AI 답변: `get_rect(center=(WIDTH//2, HEIGHT//2))` 사용.
- 적용 결과: GAME OVER 텍스트와 Retry 버튼 중앙 정렬 완료.

## 시행착오 및 해결 과정

1. 처음에는 키 입력과 이동 구현만 했음
2. 대각선 이동 속도 문제 발생 → √2로 보정
3. 화면 밖 이동 제한 구현
4. 점수 시스템 구현, 동그라미 충돌 체크
5. 10초 제한으로 Game Over 기능 추가
6. Game Over UI와 Retry 버튼 위치가 어긋남 → 중앙 정렬 적용
7. FPS와 남은 시간 UI 추가

## 배운 점

Pygame 좌표계는 y 증가가 아래 방향이며,
대각선 속도 보정은 피타고라스 정리 활용을 했다으며,
pygame.font.SysFont와 Font 차이 이해했고,
게임 루프 구조, 상태 관리(game_over 등)이 게임에 있어서 중요하다는 사실을 알 수 있었다.
이후 UI 위치 중앙 정렬 시 get_rect(center=(x,y))를 활용했고,
GitHub practice 디렉토리에 주간 기록 문서 작성 방법을 이해 했으며,
AI에 대한 이해력 상승과 효율적인 명령 방법을 배울 수 있었다.
