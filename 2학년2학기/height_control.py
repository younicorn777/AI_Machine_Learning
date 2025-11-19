from codrone_edu.drone import *
import time

# ✅ 1차원 칼만 필터 클래스 정의
class KalmanFilter1D:
    def __init__(self, Q=0.5, R=1, initial_estimate=0):
        self.Q = Q  # 시스템 예측 노이즈
        self.R = R  # 측정 노이즈
        self.x = initial_estimate  # 현재 고도 추정값
        self.P = 1.0  # 추정 오차 공분산

    def update(self, measurement):
        # 예측 단계
        self.P = self.P + self.Q

        # 칼만 이득 계산
        K = self.P / (self.P + self.R)

        # 상태 보정
        self.x = self.x + K * (measurement - self.x)

        # 공분산 갱신
        self.P = (1 - K) * self.P

        return self.x


# ✅ 드론 객체 생성 및 연결
drone = Drone()
drone.pair()

# ✅ 칼만 필터 객체 생성
kf = KalmanFilter1D(Q=0.05, R=3, initial_estimate=0)

try:
    print("이륙합니다!")
    drone.takeoff()
    time.sleep(2)

    target_z = 50   # 목표 고도 (cm)
    Kp = 1.0        # 비례 제어 상수

    print("제어 루프 시작")

    for i in range(50):
        # ✅ 센서에서 현재 고도 읽기
        raw_z = drone.get_height()
        if raw_z is None:
            raw_z = 0  # 센서 에러 처리

        # ✅ 칼만 필터로 추정 고도 계산
        filtered_z = kf.update(raw_z)

        # ✅ 비례 제어 계산
        error = target_z - filtered_z
        control = Kp * error

        # ✅ 제어 출력 제한 (안전한 범위)
        if control > 30:
            control = 30
        elif control < -30:
            control = -30

        throttle_power = int(control)

        # ✅ 현재 고도 정보 출력
        print(f"[반복 {i+1}]")
        print(f"  ▸ 센서 고도(raw):     {raw_z:.2f} cm")
        print(f"  ▸ 추정 고도(filtered): {filtered_z:.2f} cm")
        print(f"  ▸ 오차(error):         {error:.2f} cm")
        print(f"  ▸ 출력 스로틀:         {throttle_power}")
        print("------------------------------------------------")

        # ✅ 드론에 제어 명령 적용
        drone.set_throttle(throttle_power)
        drone.set_roll(0)
        drone.set_pitch(0)
        drone.set_yaw(0)

        drone.move(0.1)  # 0.1초간 명령 유지

except Exception as e:
    print("비행 중 오류 발생:", e)

finally:
    print("착륙 명령 전송...")
    drone.land()
    time.sleep(5)
    drone.close()
    print("연결 종료")