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
# 튜닝 파라미터 (여기만 바꾸면 됨)
# =========================
MOVE_POWER = 30          # 이동 세기
MOVE_MS = 800            # 이동 시간 (ms)
BRAKE_MS = 400           # 이동 후 정지 안정화 (ms)
TAKEOFF_STABILIZE_SEC = 3.0

# 드리프트 보정(hover 기준)
TRIM_ROLL = 8            # +면 오른쪽 보정
TRIM_PITCH = 8           # +면 앞으로 보정

# =========================
# 비행 상태 (중복 명령 방지)
# =========================
is_flying = False

# =========================
# 내부 유틸 (TRIM 포함 제어)
# =========================
def control_with_trim(drone, roll_val, pitch_val, yaw_val, throttle_val, duration_ms):
    """
    모든 제어에 TRIM을 기본 오프셋으로 적용.
    - roll, pitch는 TRIM이 더해짐
    - yaw, throttle은 그대로 사용
    """
    r = roll_val + TRIM_ROLL
    p = pitch_val + TRIM_PITCH
    drone.sendControlWhile(r, p, yaw_val, throttle_val, duration_ms)

# =========================
# 기본 제어 함수 (직관용)
# =========================
def roll(drone, power, duration_ms):
    control_with_trim(drone, power, 0, 0, 0, duration_ms)

def pitch(drone, power, duration_ms):
    control_with_trim(drone, 0, power, 0, 0, duration_ms)

def yaw(drone, power, duration_ms):
    # yaw에는 trim을 더하지 않음 (roll/pitch만 trim 적용)
    control_with_trim(drone, 0, 0, power, 0, duration_ms)

def throttle(drone, power, duration_ms):
    control_with_trim(drone, 0, 0, 0, power, duration_ms)

def hover(drone, duration_ms):
    # "실질적 정지" = TRIM만 적용된 상태
    control_with_trim(drone, 0, 0, 0, 0, duration_ms)

# =========================
# 미션 동작 정의
# =========================
def mission_takeoff(drone):
    global is_flying
    if is_flying:
        print("[SKIP] already flying (takeoff ignored)")
        return

    print("TakeOff")
    drone.sendTakeOff()
    sleep(TAKEOFF_STABILIZE_SEC)

    # 이륙 직후 안정화 (TRIM 기반 hover)
    hover(drone, BRAKE_MS)

    is_flying = True

def mission_land(drone):
    global is_flying
    if not is_flying:
        print("[SKIP] already landed (landing ignored)")
        # 그래도 안전 위해 1회 호출 (선택)
        drone.sendLanding()
        sleep(0.3)
        return

    print("Landing")
    for _ in range(3):
        drone.sendLanding()
        sleep(0.3)

    is_flying = False

def mission_forward(drone):
    if not is_flying:
        print("[SKIP] not flying (forward ignored)")
        return
    print("Forward")
    pitch(drone, +MOVE_POWER, MOVE_MS)
    hover(drone, BRAKE_MS)

def mission_backward(drone):
    if not is_flying:
        print("[SKIP] not flying (backward ignored)")
        return
    print("Backward")
    pitch(drone, -MOVE_POWER, MOVE_MS)
    hover(drone, BRAKE_MS)

def mission_left(drone):
    if not is_flying:
        print("[SKIP] not flying (left ignored)")
        return
    print("Move Left")
    roll(drone, -MOVE_POWER, MOVE_MS)
    hover(drone, BRAKE_MS)

def mission_right(drone):
    if not is_flying:
        print("[SKIP] not flying (right ignored)")
        return
    print("Move Right")
    roll(drone, +MOVE_POWER, MOVE_MS)
    hover(drone, BRAKE_MS)

# =========================
# 숫자 매핑 함수
# =========================
"""
제스처 숫자에 따라 미션 실행:
0 : 착륙
1 : 이륙
2 : 전진
3 : 후진
4 : 좌측 이동
5 : 우측 이동
"""

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