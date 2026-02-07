'''
02_hand_debug의 Docstring

MediaPipe를 이용한 실시간 손 인식 테스트 프로그램

MediaPipe 소개 :
1) 구글에서 만든 '실시간 기기용 머신러닝 솔루션' 
2) 직접 CNN을 설계하지 않아도 빠르고 정확한 손 인식 기능을 사용할 수 있게 해줌.

이 코드의 목적:
- 웹캠으로 입력된 영상을 기반으로 MediaPipe Hands 모듈을 사용해 손을 인식
- 손의 랜드마크(관절 위치)를 검출하고, 화면에 시각적으로 표시
- ESC 키를 누르면 프로그램을 종료

'''

import cv2
import mediapipe as mp

# MediaPipe 손 인식 초기화
mp_hands = mp.solutions.hands # 손의 21개 관절(랜드마크)을 찾는 핵심 모델
mp_draw = mp.solutions.drawing_utils # 좌표를 화면에 잘 그려주는 도구

# hands 객체 설정
'''
static_image_mode 
true : 매 프레임마다 새로운 손을 찾음 => 연산량 증가
false : 한번 찾은 손을 추적 => 연산량 감소, 실시간 처리에 유리
'''
hands = mp_hands.Hands(
    static_image_mode=False,        # 영상 스트림 모드 (False: 실시간 처리)
    max_num_hands=1,                # 최대 인식 손 개수
    min_detection_confidence=0.7,   # 70% 이상의 확신이 들 때만 '손'이라고 판단
    min_tracking_confidence=0.7     # 검출된 손을 계속 따라갈 때의 신뢰도 기준
)

# 웹캠 열기
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("카메라를 열 수 없습니다.")
    exit()

print("손 인식 테스트 시작. ESC 키로 종료")

while True:
    ret, frame = cap.read()
    if not ret:
        print("프레임을 읽을 수 없습니다.")
        break

    # BGR → RGB (MediaPipe는 RGB 필수)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # 손 인식 : 손의 위치와 21개 관절 좌표 계산
    result = hands.process(rgb)

    # 손 랜드마크가 검출된 경우
    '''
    multi_hand_landmarks: 검출된 손들의 좌표 리스트
    hand_landmarks: 하나의 손당 21개의 좌표(x, y, z) / (z값은 카메라로부터의 거리를 나타내는 상대적 깊이)
    HAND_CONNECTIONS: 관절끼리 선으로 연결
    '''
    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            # 손 랜드마크 그리기
            mp_draw.draw_landmarks(
                frame,                      # 출력할 프레임
                hand_landmarks,             # 손 랜드마크 좌표
                mp_hands.HAND_CONNECTIONS   # 랜드마크 연결선
            )

    cv2.imshow("Hand Debug", frame)

    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()