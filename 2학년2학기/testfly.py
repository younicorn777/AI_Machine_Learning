from codrone_edu.drone import *
import time

# --- 1. 전진 속도용 칼만 필터 (X축) ---
class KalmanFilterVelocityX:
    # ... (이 부분은 변경 없음)
    def __init__(self, initial_velocity=0):
        self.velocity = initial_velocity
        self.P = 1.0
        self.Q = 0.01
        self.R = 0.5

    def update(self, accel, flow_velocity, dt):
        pred_velocity = self.velocity + (accel * dt)
        pred_P = self.P + self.Q
        K = pred_P / (pred_P + self.R)
        self.velocity = pred_velocity + K * (flow_velocity - pred_velocity)
        self.P = (1 - K) * pred_P
        return self.velocity

# --- 2. 측면 속도용 칼만 필터 (Y축) ---
class KalmanFilterVelocityY:
    # ... (이 부분은 변경 없음)
    def __init__(self, initial_velocity=0):
        self.velocity = initial_velocity
        self.P = 1.0
        self.Q = 0.01
        self.R = 0.5

    def update(self, accel, flow_velocity, dt):
        pred_velocity = self.velocity + (accel * dt)
        pred_P = self.P + self.Q
        K = pred_P / (pred_P + self.R)
        self.velocity = pred_velocity + K * (flow_velocity - pred_velocity)
        self.P = (1 - K) * pred_P
        return self.velocity


# --- 3. 고도용 칼만 필터 (R/Q 값 수정) ---
class KalmanFilterHeight:
    def __init__(self, initial_estimate=0):
        self.x = initial_estimate
        self.P = 1.0
        self.Q = 0.15 # Q 값 증가: 상태 변화를 조금 더 신뢰
        self.R = 1.5  # R 값 감소: 측정값을 조금 더 신뢰 (필터 반응 속도 증가) 

    def update(self, measurement):
        self.P = self.P + self.Q
        K = self.P / (self.P + self.R)
        self.x = self.x + K * (measurement - self.x)
        self.P = (1 - K) * self.P
        return self.x


# --- 메인 실행 ---
drone = Drone()
drone.pair()

kf_vel_x = KalmanFilterVelocityX()
kf_vel_y = KalmanFilterVelocityY()
kf_h = KalmanFilterHeight()

# [중요] 값 보정을 위한 변수들
accel_offset_x = 0
accel_offset_y = 0 
SCALE_ACCEL = 0.012
SCALE_FLOW = 0.006

# [핵심 수정] 고도 제어 게인 (KP 값 낮춤)
ALTITUDE_KP = 0.7 


try:
    # 1. 캘리브레이션 (0점 잡기)
    print("센서 0점 조절 중... 드론을 건드리지 마세요.")
    sum_accel_x = 0
    sum_accel_y = 0
    for _ in range(20):
        sum_accel_x += drone.get_accel_x()
        sum_accel_y += drone.get_accel_y()
        time.sleep(0.05)
    accel_offset_x = sum_accel_x / 20
    accel_offset_y = sum_accel_y / 20
    print(f"0점 완료. X 오프셋: {accel_offset_x:.1f}, Y 오프셋: {accel_offset_y:.1f}")

    print("이륙합니다!")
    drone.takeoff()
    time.sleep(2)

    # --- 1단계: 전진 460cm ---
    print("--- ✈️ 1단계: 전진 460cm 시작 ---")
    target_dist_x = 465
    target_z = 150
    current_dist_x = 0
    last_time = time.time()
    
    # 목표 고도 설정 (안정적인 고도 유지를 위한 추가 Throttle)
    # 드론이 고도를 유지하는 기본 스로틀을 찾고, P 제어를 보정값으로 사용
    
    while current_dist_x < target_dist_x:
        current_time = time.time()
        dt = current_time - last_time
        last_time = current_time

        # 1) 고도 필터링
        raw_z = drone.get_height()
        filtered_z = kf_h.update(raw_z)

        # 2) 전진 속도 계산 (X축)
        raw_accel_x = drone.get_accel_x()
        calibrated_accel_x = (raw_accel_x - accel_offset_x) * SCALE_ACCEL
        raw_flow_x = drone.get_flow_velocity_x()
        scaled_flow_x = raw_flow_x * SCALE_FLOW
        
        real_velocity_x = kf_vel_x.update(calibrated_accel_x, scaled_flow_x, dt)
        current_dist_x += real_velocity_x * dt

        # --- 제어 ---
        # 수정: ALTITUDE_KP (0.7) 적용
        throttle = int(ALTITUDE_KP * (target_z - filtered_z))
        throttle = max(-20, min(30, throttle)) # 12/03 max : -30 -> -20 
        
        pitch = 25 # 전진
        roll = 0   

        drone.set_throttle(throttle)
        drone.set_pitch(pitch)
        drone.set_roll(roll)
        drone.move()
        
        print(f"[1단계] 거리(X): {current_dist_x:.1f} / {target_dist_x} | 속도(X): {real_velocity_x:.1f} | 필터고도: {filtered_z:.1f} | Throttle: {throttle}")
        time.sleep(0.05)
    
    # 1단계 완료: 잠시 정지
    drone.set_pitch(0)
    drone.move()
    print("--- ✅ 1단계 완료: 전진 460cm 도착 ---")
    time.sleep(1)


    # --- 2단계: 우측 690cm 이동 ---
    print("--- ➡️ 2단계: 우측 690cm 이동 시작 ---")
    target_dist_y = 715 
    current_dist_y = 0
    last_time = time.time()

    while current_dist_y < target_dist_y:
        current_time = time.time()
        dt = current_time - last_time
        last_time = current_time

        # 1) 고도 필터링
        raw_z = drone.get_height()
        filtered_z = kf_h.update(raw_z)

        # 2) 측면 속도 계산 (Y축)
        raw_accel_y = drone.get_accel_y()
        calibrated_accel_y = (raw_accel_y - accel_offset_y) * SCALE_ACCEL
        raw_flow_y = drone.get_flow_velocity_y()
        scaled_flow_y = raw_flow_y * SCALE_FLOW
        
        real_velocity_y = kf_vel_y.update(calibrated_accel_y, scaled_flow_y, dt)
        current_dist_y += abs(real_velocity_y * dt) 

        # --- 제어 ---
        # 수정: ALTITUDE_KP (0.7) 적용
        throttle = int(ALTITUDE_KP * (target_z - filtered_z))
        throttle = max(-30, min(30, throttle))
        
        pitch = 0  
        roll = 25  # 우측 이동 (Roll 양수)

        drone.set_throttle(throttle)
        drone.set_pitch(pitch)
        drone.set_roll(roll)
        drone.move()

        print(f"[2단계] 거리(Y): {current_dist_y:.1f} / {target_dist_y} | 속도(Y): {real_velocity_y:.1f} | 필터고도: {filtered_z:.1f} | Throttle: {throttle}")
        time.sleep(0.05)
        
    # 2단계 완료: 잠시 정지
    drone.set_roll(0)
    drone.move()
    print("--- ✅ 2단계 완료: 우측 690cm 도착 ---")
    time.sleep(1)


    # --- 3단계: 착륙 ---
    print("최종 목적지 도착! 착륙합니다.")
    drone.land()

except Exception as e:
    print("오류:", e)
    drone.land()

finally:
    drone.close()