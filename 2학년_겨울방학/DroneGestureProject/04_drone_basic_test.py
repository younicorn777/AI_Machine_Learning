'''
04_drone_basic_test의 Docstring

드론 기본 비행 제어 프로그램

이 코드의 목적:
- 드론과 연결하여 이륙, 이동(roll, pitch, yaw, throttle), 호버링, 착륙을 제어
- 축 제어 함수를 별도로 정의해 직관적으로 드론을 움직일 수 있도록 구성
- 안전을 위해 예외 처리(KeyboardInterrupt, 일반 Exception) 시 즉시 착륙하도록 함
'''

from time import sleep
from e_drone.drone import *
from e_drone.protocol import *

# =========================
# 축 제어 함수 정의
# =========================

def roll(drone, power, duration):
    drone.sendControlWhile(power, 0, 0, 0, duration)

def pitch(drone, power, duration):
    drone.sendControlWhile(0, power, 0, 0, duration)

def yaw(drone, power, duration):
    drone.sendControlWhile(0, 0, power, 0, duration)

def throttle(drone, power, duration):
    drone.sendControlWhile(0, 0, 0, power, duration)

def hover(drone, duration):
    drone.sendControlWhile(0, 0, 0, 0, duration)

# =========================
# 실행
# =========================
if __name__ == '__main__':
    drone = Drone() # 드론 객체 생성
    
    # 드론 연결 시도
    if drone.open():
        print("Connected Success!")
        sleep(0.01) # 연결 후 잠시 대기
    else:
        print("Connection Failed...")
        exit()

    try:
        # 이륙
        print("TakeOff - Waiting for 5 seconds to stabilize")
        drone.sendTakeOff()
        sleep(5)

        # 예시 동작 (주석 처리된 부분은 필요 시 활성화)
    
        # 앞/뒤로 움직임 테스트

        print("Hover for 3 seconds")
        hover(drone, 3000)

        print("Forward 2 seconds")
        pitch(drone, 20, 2000)

        print("Hover for 3 seconds")
        hover(drone, 3000)

        print("Backward 2 seconds")
        pitch(drone, -20, 2000)

        print("Hover for 3 seconds")
        hover(drone, 3000)
        
        '''
        # 좌/우로 움직임 테스트

        print("Hover for 3 seconds")
        hover(drone, 3000)
        
        print("Move left 2 seconds")
        roll(drone, -30, 2000)

        print("Hover for 3 seconds")
        hover(drone, 3000)
        
        print("Move right 2 seconds")
        roll(drone, 30, 2000)

        print("Hover for 2 seconds")
        hover(drone, 2000)
        '''

        '''
        #시계/반시계 방향 회전 테스트

        print("Hover for 3 seconds")
        hover(drone, 3000)

        print("Turn Right 3 seconds")
        yaw(drone, -50, 3000)

        print("Hover for 3 seconds")
        hover(drone, 3000)

        print("Turn Left 3 seconds")
        yaw(drone, 50, 3000)
        '''

        # 안전을 위해 착륙 명령을 여러 번 실행 
        print("Landing")
        drone.sendLanding()
        sleep(1)
        drone.sendLanding()
        sleep(1)

    # 사용자가 Ctrl+C 누르면, 즉시 착륙
    except KeyboardInterrupt:
        print("\n[STOP] User forced stop -> Emergency Landing")
        for _ in range(2):       
            drone.sendLanding()
            sleep(0.01)

    # 그 외 모든 에러 발생 시, 즉시 착륙       
    except Exception as e:
        print(f"[ERROR] {e}")
        for _ in range(2):       
            drone.sendLanding()
            sleep(0.01)
    
    # 어떤 상황에서도 통신 종료
    finally:
        print("Closing connection")
        drone.close()           
