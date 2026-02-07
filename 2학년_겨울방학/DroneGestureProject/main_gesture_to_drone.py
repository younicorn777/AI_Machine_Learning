'''
main_gesture_to_drone의 Docstring

MediaPipe 손 제스처 기반 드론 제어 프로그램

이 코드의 목적:
- 웹캠으로 손을 인식하고, 손가락 개수를 계산하여 제스처를 숫자로 변환
- 같은 제스처가 일정 시간(3초) 동안 유지되면 '확정'으로 판단
- 확정된 제스처 숫자를 드론 미션 함수에 매핑하여 자동으로 드론을 제어
- 안전을 위해 시작 시 착륙 명령을 반복하고, 종료 시에도 착륙 후 연결을 종료

'''

import cv2
import mediapipe as mp
import time
import math
from time import sleep

from e_drone.drone import *
from e_drone.protocol import *

import drone_missions

# =========================
# MediaPipe 설정
# =========================
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# =========================
# 손가락 개수 계산 (엄지 개선 버전)
# =========================
def count_fingers(hand_landmarks):
    # 1) 검지/중지/약지/소지 (y좌표 비교)
    finger_tips = [8, 12, 16, 20]
    count = 0
    for tip in finger_tips:
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[tip - 2].y:
            count += 1

    # 2) 엄지(거리 기반)
    thumb_tip = hand_landmarks.landmark[4]
    thumb_base = hand_landmarks.landmark[2]
    pinky_base = hand_landmarks.landmark[17]

    def get_dist(p1, p2):
        return math.hypot(p1.x - p2.x, p1.y - p2.y)

    dist_tip_to_pinky = get_dist(thumb_tip, pinky_base)
    dist_base_to_pinky = get_dist(thumb_base, pinky_base)

    if dist_tip_to_pinky > dist_base_to_pinky:
        count += 1

    return count

# =========================
# 안정성 판단 설정
# =========================
STABLE_TIME = 3.0       # 같은 제스처 3초 유지 시 확정

candidate_gesture = None   # 현재 후보 제스처
candidate_start_time = 0.0 # 후보 시작 시간

gesture_active = False 

# =========================
# 드론 연결
# =========================
drone = Drone()

if drone.open():
    print("Connected Success!")
    sleep(0.5)
else:
    print("Connection Failed...")
    exit()

# (안전) 시작 전에 착륙 + hover(제어값 초기화)로 상태 정리
for _ in range(2):
    drone.sendLanding()
    sleep(0.3)
drone.sendControlWhile(0, 0, 0, 0, 300)
sleep(0.3)

# =========================
# 카메라 시작
# =========================
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("카메라를 열 수 없습니다.")
    drone.close()
    exit()

print("Gesture -> Drone control started (ESC 종료)")

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb)

        gesture = None
        
        # =========================
        # 손 인식
        # =========================
        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                # 손 랜드마크 그리기
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                # 손가락 개수 계산
                gesture = count_fingers(hand_landmarks)

        # 0 ~ 5만 인정 (그 외는 무시)
        if gesture is not None and (gesture < 0 or gesture > 5) :
            gesture = None

        now = time.time()

        # =========================
        # 화면 표시 영역
        # =========================

        # 1. 드론 상태 표시 (FLYING / LANDED)
        flight_text = "FLYING" if drone_missions.is_flying else "LANDED"
        cv2.putText(frame, f"Drone State: {flight_text}",
                            (10, 35), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 0), 2)
        
        # 2. 현재 인식된 제스처
        gesture_text = "NONE" if gesture is None else str(gesture)
        cv2.putText( frame, f"Gesture Now : {gesture_text}",
                            (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2) 
        
        # =========================
        # 안정성 로직 (Edge Trigger)
        # =========================
        if gesture is not None:
             # 새로운 제스처 등장 시 후보 갱신
            if candidate_gesture is None or gesture != candidate_gesture:
                candidate_gesture = gesture
                candidate_start_time = now
            else:
                elapsed = now - candidate_start_time

                cv2.putText( frame, f"Stable Time : {elapsed:.1f}s",
                                        (10, 105), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

                # 안정성 만족 + 아직 실행 안했을 때만 실행
                if elapsed >= STABLE_TIME and not gesture_active:
                    print(f"[CONFIRMED] {gesture}")
                    drone_missions.execute_mission(drone, gesture) # 제스처 숫자 -> 드론 미션 실행

                    # 실행 직후 후보 리셋
                    candidate_gesture = None
                    candidate_start_time = 0.0
                    gesture_active = True # 실행 후 잠금

                    # 0번 : 착륙 후 종료
                    if gesture == 0 :
                        print("Landing and Exit")
                        sleep(1.0)
                        break

        # ===== 손이 안 보이면, 잠금 해제 =====                    
        else:
            candidate_gesture = None
            gesture_active = False

        # 결과 화면 출력
        cv2.imshow("Gesture Control", frame)

        # ESC 키 입력 시 종료
        if cv2.waitKey(1) & 0xFF == 27:
            break

except KeyboardInterrupt:
    print("\n[STOP] User forced stop -> Landing")

finally:
    # 종료 시 안전 착륙
    for _ in range(2):
        drone.sendLanding()
        sleep(0.5)

    cap.release()
    cv2.destroyAllWindows()
    drone.close()
    print("Closed.")