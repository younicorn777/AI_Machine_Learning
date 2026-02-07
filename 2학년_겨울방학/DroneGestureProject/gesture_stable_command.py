'''
03_gesture_stable_command의 Docstring

MediaPipe를 이용한 손가락 개수 기반 제스처 인식 프로그램

이 코드의 목적:
- 웹캠으로 입력된 영상을 기반으로 손을 인식
- 손가락이 몇 개 펴져 있는지 계산하여 제스처를 숫자로 표현
- 같은 제스처가 일정 시간(3초) 동안 유지되면 '확정'으로 표시
- ESC 키를 누르면 프로그램을 종료

[MediaPipe에서 손의 랜드마크(21개)]

* 각 랜드마크(특징점?)마다 x,y,z 값이 있음 

1. x와 y : 화면상의 위치 (Normalized Coordinates)
- 주의할 점 : 이 값들이 픽셀 단위(예: 640, 480)가 아니라 0.0 ~ 1.0 사이로 정규화된 값
- x: 이미지의 너비(Width)를 기준으로 한 상대적 위치
  (0.0은 화면의 왼쪽 끝, 1.0은 오른쪽 끝을 의미)
- y: 이미지의 높이(Height)를 기준으로 한 상대적 위치
  (0.0은 화면의 위쪽 끝, 1.0은 아래쪽 끝을 의미)

2. z : 상대적 깊이 (Landmark Depth)
- 일반 카메라(2D)를 사용함에도 불구하고 딥러닝 모델이 상대적인 깊이를 추측
- 의미: 손목(0번 랜드마크)을 기준으로 해당 마디가 카메라와 얼마나 가까운지를 나타냄
- 기준: 손목(Wrist)의 z값이 0. 
- 값의 해석 : 값이 작을수록(음수) 카메라와 더 가깝고, 값이 클수록(양수) 카메라에서 더 멂
- 주의: 이 값은 실제 단위의 거리가 아니라, 손목 주위의 상대적인 두께/깊이를 나타내는 수치

'''

import cv2
import mediapipe as mp
import time
import math

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("카메라를 열 수 없습니다.")
    exit()

# 안정성 관련 변수
candidate_gesture = None    # 현재 후보 제스처
candidate_start_time = 0.0  # 후보 제스처가 유지되기 시작한 시간
STABLE_TIME = 3.0           # 같은 제스처가 3초 유지되어야 확정


def count_fingers(hand_landmarks):
    # 1. 나머지 네 손가락 (y좌표 비교)
    finger_tips = [8, 12, 16, 20]
    count = 0
    for tip in finger_tips:
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[tip - 2].y:
            count += 1

    # 2. 엄지 판별 로직 개선 (상대적 거리 이용)
    # 엄지 끝(4번)과 소지 뿌리(17번) 사이의 거리를 측정
    # 이 거리가 엄지 뿌리(2번)와 소지 뿌리(17번) 사이의 거리보다 멀면 펴진 것으로 간주
    
    thumb_tip = hand_landmarks.landmark[4]
    thumb_base = hand_landmarks.landmark[2]
    pinky_base = hand_landmarks.landmark[17]

    # 거리 계산 함수 (유클리드 거리)
    def get_dist(p1, p2):
        return math.hypot(p1.x - p2.x, p1.y - p2.y)

    dist_tip_to_pinky = get_dist(thumb_tip, pinky_base)
    dist_base_to_pinky = get_dist(thumb_base, pinky_base)

    if dist_tip_to_pinky > dist_base_to_pinky:
        count += 1

    return count

print("제스처 안정성 테스트 시작 (ESC 종료)")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    gesture = None # 현재 프레임에서 인식된 제스처

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_draw.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS
            )
            # 손가락 개수 계산 -> 제스처 숫자
            gesture = count_fingers(hand_landmarks)

    now = time.time() # 현재 시간

    # ===== 안정성 판단 =====

    if gesture is not None:
        # 새로운 제스처가 등장하면 후보 갱신
        if candidate_gesture is None or gesture != candidate_gesture:
            candidate_gesture = gesture
            candidate_start_time = now
        else:
            elapsed = now - candidate_start_time # 같은 제스처가 유지된 시간 계산
            
            # 화면에 안정성 시간 표시
            cv2.putText(
                frame,
                f"Gesture {gesture} stable: {elapsed:.1f}s",
                (10, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 0),
                2
            )

            # 안정성 시간 충족 시 확정 표시
            if elapsed >= STABLE_TIME:
                cv2.putText(
                    frame,
                    f"CONFIRMED: Gesture {gesture}",
                    (10, 80),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 0, 255),
                    2
                )
    else:
        candidate_gesture = None # 손이 인식되지 않으면 후보 초기화

    # 결과 화면 출력
    cv2.imshow("Gesture Stable Command", frame)

    # ESC 키 입력 시 종료
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
