'''
drone_missions의 Docstring

이 코드의 목적:
- 드론과 연결하여 기본적인 축 제어(roll, pitch, yaw, throttle, hover)를 수행
- 특정 미션 동작(이륙, 착륙, 전진, 후진, 좌측 이동, 우측 이동)을 함수로 정의
- 손 제스처의 숫자 입력(gesture_number)에 따라 해당 미션을 실행할 수 있도록 매핑
- 비행 상태 플래그(is_flying)를 두어 중복 명령을 방지하고, 안전한 제어를 구현
'''

from time import sleep
from e_drone.drone import *
from e_drone.protocol import *

# =========================
# 튜닝 파라미터 
# =========================

HOVER_MS = 1000  # 호버링 유지 시간(ms)

TRIM_ROLL = 3    # 호버링 시, Roll 보정값
TRIM_PITCH = 12  # 호버링 시, Pitch 보정값

TAKEOFF_STABILIZE_SEC = 3.0 # 이륙 후 안정화 대기 시간(sec)

# =========================
# 비행 상태 (중복 명령 방지)
# =========================
is_flying = False   # 현재 드론이 비행 중인지 여부

# =========================
# 기본 제어
# control : TRIM 없이 순수 제어값 전달 (호버링/이동/브레이크에 사용)
# hover : TRIM 보정값 만 적용
# brake : 관성 제거용 브레이크 (반대 방향으로 짧게)
# =========================
def control(drone, roll, pitch, yaw, throttle, duration_ms):
    drone.sendControlWhile(roll, pitch, yaw, throttle, duration_ms)

def hover(drone, duration_ms):
    print("Hover")
    control(drone, TRIM_ROLL, TRIM_PITCH, 0, 0, duration_ms)

def brake(drone, roll, pitch, duration_ms):
    print("Brake")
    control(drone, roll, pitch, 0, 0, duration_ms)

# =========================
# 미션 (이동 -> 브레이크 -> 호버)
# =========================
def mission_takeoff(drone):
    global is_flying
    if is_flying:
        print("[SKIP] already flying (takeoff ignored)")
        return

    print("TakeOff")
    drone.sendTakeOff()
    sleep(TAKEOFF_STABILIZE_SEC)

    # 이륙 직후 안정화
    hover(drone, 1000)
    is_flying = True

def mission_land(drone):
    global is_flying

    print("Landing")
    for _ in range(3):
        drone.sendLanding()
        sleep(0.5)

    is_flying = False

def mission_forward(drone):
    if not is_flying:
        print("[SKIP] not flying (forward ignored)")
        return

    print("Forward")
    control(drone, 0, 40, 0, 0, 3000)
    brake(drone, 0, -15, 500)
    hover(drone, HOVER_MS)

def mission_backward(drone):
    if not is_flying:
        print("[SKIP] not flying (backward ignored)")
        return

    print("Backward")
    control(drone, 0, -30, 0, 0, 2000)
    brake(drone, 0, +10, 700)
    hover(drone, HOVER_MS)

def mission_left(drone):
    if not is_flying:
        print("[SKIP] not flying (left ignored)")
        return

    print("Left")
    control(drone, -30, 0, 0, 0, 2000)
    brake(drone, +10, 0, 700)
    hover(drone, HOVER_MS)

def mission_right(drone):
    if not is_flying:
        print("[SKIP] not flying (right ignored)")
        return

    print("Right")
    control(drone, +30, 0, 0, 0, 2000)
    brake(drone, -10, 0, 700)
    hover(drone, HOVER_MS)

# =========================
# 안전 초기화 루틴
# 방법 : 
# 1) 공중 상태로 남아 있을 경우 대비 : 착륙 명령
# 2) 제어값 초기화
# =========================
def safe_initialize(drone):
    global is_flying

    print("[INIT] Resetting drone state...")

    # 혹시 공중에 떠 있을 가능성 대비
    for _ in range(3):
        drone.sendLanding()
        sleep(0.5)

    # 제어값 초기화
    hover(drone, 500)
    sleep(0.5)

    is_flying = False

    print("[INIT] Reset complete.")

# =========================
# 제스처 숫자 -> 미션 매핑
# 0 : 착륙
# 1 : 이륙
# 2 : 전진
# 3 : 후진
# 4 : 좌측
# 5 : 우측
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