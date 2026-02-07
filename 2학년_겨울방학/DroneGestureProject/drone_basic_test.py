'''
04_drone_basic_test의 Docstring

드론 기본 비행 제어 프로그램

이 코드의 목적:
- 드론과 연결하여 이륙, 이동(roll, pitch, yaw, throttle), 호버링, 착륙을 제어
- 축 제어 함수를 별도로 정의해 직관적으로 드론을 움직일 수 있도록 구성
- 안전 초기화 루틴(safe_initialize)과 안전 착륙 루틴(safe_land)을 추가하여,
  예기치 못한 상황에서도 드론을 안전하게 제어할 수 있도록 함
- 안전을 위해 예외 처리(KeyboardInterrupt, 일반 Exception) 시 즉시 착륙하도록 함
'''

from time import sleep
from e_drone.drone import *
from e_drone.protocol import *

# =========================
# 축 제어 함수 정의
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
# 안전 초기화 루틴
# 방법 : 
# 1) 공중 상태로 남아 있을 경우 대비 : 착륙 명령
# 2) 제어값 초기화
# =========================

def safe_initialize(drone):
    print("[INIT] Resetting drone state...")

    # 혹시 공중 상태로 남아있을 가능성 대비
    for _ in range(3):
        drone.sendLanding()
        sleep(0.3)

    # 제어값 0으로 덮어쓰기 (제어값 초기화)(호버 명령으로 초기화)
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

        print("Hover 2s")
        hover(drone, 2000)

        # 예시 동작 (주석 처리된 부분은 필요 시 활성화)
        # 앞/뒤로 움직임 테스트
        print("Forward 2s")
        pitch(drone, 30, 2000)  
        print("Hover 2s")
        hover(drone, 2000)

        print("Backward 2s")
        pitch(drone, -30, 2000)
        print("Hover 2s")
        hover(drone, 2000)

        """
        # 좌/우로 움직임 테스트

        print("Move Left 2s")
        roll(drone, -30, 2000)
        hover(drone, 2000)

        print("Move Right 2s")
        roll(drone, 30, 2000)
        hover(drone, 2000)
        """

        """
        #시계/반시계 방향 회전 테스트

        print("Rotate CW 2s")
        yaw(drone, -30, 2000)
        hover(drone, 2000)

        print("Rotate CCW 2s")
        yaw(drone, 30, 2000)
        hover(drone, 2000)
        """

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
        drone.close()