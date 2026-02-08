'''
drone_basic_test의 Docstring

드론 기본 비행 제어 프로그램

이 코드의 목적:
- 드론과 연결하여 이륙, 이동(roll, pitch, yaw, throttle), 호버링, 착륙을 제어
- 축 제어 함수를 별도로 정의해 직관적으로 드론을 움직일 수 있도록 구성
- 이동 시 관성 제어(Brake)를 추가하여 보다 안정적인 제어를 구현
- 안전 초기화 루틴(safe_initialize)과 안전 착륙 루틴(safe_land)을 추가하여,
  예기치 못한 상황에서도 드론을 안전하게 제어할 수 있도록 함
- 안전을 위해 예외 처리(KeyboardInterrupt, 일반 Exception) 시 즉시 착륙하도록 함
'''

from time import sleep
from e_drone.drone import *
from e_drone.protocol import *

# =========================
# 튜닝 파라미터
# =========================
MOVE_POWER = 30       # 기본 이동 파워  
MOVE_MS = 1000        # 이동 시간(ms)

BRAKE_POWER = 20      # 관성 제어 세기
BRAKE_MS = 500        # 관성 제어 시간

HOVER_MS = 1000       # 호버링 유지 시간(ms)

TRIM_ROLL = 5         # 드론 Roll 보정값
TRIM_PITCH = 8        # 드론 Pitch 보정값

'''
TRIM_ROLL / TRIM_PITCH 기록
1차 : 10 / 12
2차 : 5 / 8 => 최적
''' 

# =========================
# 기본 제어
# control : 드론 제어 명령
# hover : 드론 호버링 (보정값 적용)
# =========================
def control(drone, roll, pitch, yaw, throttle, duration_ms):
    drone.sendControlWhile(roll, pitch, yaw, throttle, duration_ms)

def hover(drone, duration_ms):
    control(drone, TRIM_ROLL, TRIM_PITCH, 0, 0, duration_ms)

# =========================
# 이동 + 관성 제어
# =========================
def move_forward(drone):
    print("Forward")
    control(drone, 0, MOVE_POWER, 0, 0, MOVE_MS)

    # 관성 제어 (반대 방향)
    print("Brake")
    control(drone, 0, -BRAKE_POWER, 0, 0, BRAKE_MS)

    hover(drone, HOVER_MS)

def move_backward(drone):
    print("Backward")
    control(drone, 0, -MOVE_POWER, 0, 0, MOVE_MS)

    print("Brake")
    control(drone, 0, BRAKE_POWER, 0, 0, BRAKE_MS)

    hover(drone, HOVER_MS)

def move_left(drone):
    print("Left")
    control(drone, -MOVE_POWER, 0, 0, 0, MOVE_MS)

    print("Brake")
    control(drone, BRAKE_POWER, 0, 0, 0, BRAKE_MS)

    hover(drone, HOVER_MS)

def move_right(drone):
    print("Right")
    control(drone, MOVE_POWER, 0, 0, 0, MOVE_MS)

    print("Brake")
    control(drone, -BRAKE_POWER, 0, 0, 0, BRAKE_MS)

    hover(drone, HOVER_MS)

# =========================
# 안전 초기화 루틴
# 방법 : 
# 1) 공중 상태로 남아 있을 경우 대비 : 착륙 명령
# 2) 제어값 초기화
# =========================

def safe_initialize(drone):
    print("[INIT] Resetting drone state...")

    # 혹시 공중 상태로 남아있을 가능성 대비
    safe_land(drone)

    # 제어값 0으로 덮어쓰기 (호버 명령으로 제어값 초기화)
    hover(drone, 500)
    sleep(0.5)

    print("[INIT] Reset complete.")

# =========================
# 안전 착륙 루틴
# 방법 : 착륙 명령을 여러 번 반복
# =========================

def safe_land(drone):
    print("[SAFE] Landing sequence...")

    for _ in range(3):
        drone.sendLanding()
        sleep(0.5)

# =========================
# 실행
# =========================

if __name__ == '__main__':

    drone = Drone() # 드론 객체 생성

    # 드론 연결 시도
    if drone.open():
        print("Connected Success!")
        sleep(0.5) # 연결 후 잠시 대기
    else:
        print("Connection Failed...")
        exit()

    try:
        # 상태 초기화
        safe_initialize(drone)

        # 이륙
        print("TakeOff")
        drone.sendTakeOff()
        sleep(3)

        print("Hover 5s")
        hover(drone, 5000)

        # 예시 동작 
        # 앞/뒤로 움직임 테스트
        print("Forward 2s")
        move_forward(drone)
        sleep(0.01)

        print("Backward 2s")
        move_backward(drone)
        sleep(0.01)

        # 좌/우로 움직임 테스트    
        print("Left 2s")    
        move_left(drone)
        sleep(0.01)

        print("Right 2s")
        move_right(drone)
        sleep(0.01)

        # 정상 착륙
        safe_land(drone)

    # 사용자가 Ctrl+C 누르면, 즉시 착륙
    except KeyboardInterrupt:
        print("\n[STOP] Emergency Landing (KeyboardInterrupt)")
        safe_land(drone)

    # 그 외 모든 에러 발생 시, 즉시 착륙
    except Exception as e:
        print(f"[ERROR] {e}")
        safe_land(drone)

    # 어떤 상황에서도 통신 종료
    finally:
        print("Closing connection")
        for _ in range(3):
            drone.close()
            sleep(0.5)