'''
05_drone_missions의 Docstring

이 코드의 목적:
- 드론과 연결하여 기본적인 축 제어(roll, pitch, yaw, throttle, hover)를 수행
- 특정 미션 동작(이륙, 착륙, 전진, 후진, 좌측 이동, 우측 이동)을 함수로 정의
- 손 제스처의 숫자 입력(gesture_number)에 따라 해당 미션을 실행할 수 있도록 매핑

'''

from time import sleep
from e_drone.drone import *
from e_drone.protocol import *

# =========================
# 튜닝 파라미터 
# =========================
MOVE_POWER = 30
MOVE_MS = 800
BRAKE_MS = 1000
TAKEOFF_STABILIZE_SEC = 3.0

# =========================
# 비행 상태 (중복 명령 방지)
# =========================
is_flying = False

# =========================
# 기본 제어 함수
# =========================

def roll(drone, power, duration_ms):
    drone.sendControlWhile(power, 0, 0, 0, duration_ms)

def pitch(drone, power, duration_ms):
    drone.sendControlWhile(0, power, 0, 0, duration_ms)

def yaw(drone, power, duration_ms):
    drone.sendControlWhile(0, 0, power, 0, duration_ms)

def throttle(drone, power, duration_ms):
    drone.sendControlWhile(0, 0, 0, power, duration_ms)

def hover(drone, duration_ms):
    drone.sendControlWhile(0, 0, 0, 0, duration_ms)

# =========================
# 미션 동작 정의
# =========================

# 이륙
def mission_takeoff(drone):
    global is_flying
    if is_flying:
        print("[SKIP] already flying (takeoff ignored)")
        return

    print("TakeOff")
    drone.sendTakeOff()
    sleep(TAKEOFF_STABILIZE_SEC)
    hover(drone, BRAKE_MS)
    is_flying = True

# 착륙
def mission_land(drone):
    global is_flying
    if not is_flying:
        print("[SKIP] already landed (landing ignored)")
        # 그래도 안전을 위해 1회는 호출
        drone.sendLanding()
        sleep(0.5)
        return

    print("Landing")
    drone.sendLanding()
    sleep(1.0)
    drone.sendLanding()
    sleep(1.0)
    is_flying = False

# 전진 
def mission_forward(drone):
    if not is_flying:
        print("[SKIP] not flying (forward ignored)")
        return
    print("Forward")
    pitch(drone, +MOVE_POWER, MOVE_MS)
    hover(drone, BRAKE_MS)

# 후진
def mission_backward(drone):
    if not is_flying:
        print("[SKIP] not flying (backward ignored)")
        return
    print("Backward")
    pitch(drone, -MOVE_POWER, MOVE_MS)
    hover(drone, BRAKE_MS)

# 좌측 이동
def mission_left(drone):
    if not is_flying:
        print("[SKIP] not flying (left ignored)")
        return
    print("Move Left")
    roll(drone, -MOVE_POWER, MOVE_MS)
    hover(drone, BRAKE_MS)

# 우측 이동
def mission_right(drone):
    if not is_flying:
        print("[SKIP] not flying (right ignored)")
        return
    print("Move Right")
    roll(drone, +MOVE_POWER, MOVE_MS)
    hover(drone, BRAKE_MS)

# =========================
# 숫자 매핑 함수
"""
    제스처 숫자에 따라 미션 실행:
    0 : 착륙
    1 : 이륙
    2 : 전진
    3 : 후진
    4 : 좌측 이동
    5 : 우측 이동
"""
# =========================

def execute_mission(drone, gesture_number):

    if gesture_number == 0:
        mission_land(drone)

    elif gesture_number == 1:
        mission_takeoff(drone)

    elif gesture_number == 2:
        mission_forward(drone)

    elif gesture_number == 3:
        mission_backward(drone)

    elif gesture_number == 4:
        mission_left(drone)

    elif gesture_number == 5:
        mission_right(drone)

    else:
        print("[NO MAP] gesture:", gesture_number)