'''
digit_predict_live_stable의 Docstring

실시간 손글씨 숫자 인식 + 아두이노 전송 프로그램

이 코드의 목적:
- 웹캠으로 입력된 손글씨 숫자를 CNN(MNIST 학습 모델)로 인식
- 인식된 숫자가 일정 시간(3.5초) 동안 안정적으로 유지될 때만 '확정'으로 판단
- 확정된 숫자를 아두이노로 시리얼 통신을 통해 전송
- 숫자가 0으로 확정되면 시스템을 중단한다 (STOP_ON_ZERO)

** 주의사항 : 노트북에 전원 연결하고, 외부 전원은 연결하지 않은 상태로 진행 **
'''

import cv2 # 카메라 열기, 이미지 처리용
import numpy as np # 이미지 배열 계산용
import tensorflow as tf # 학습된 cnn 모델 불러와서 예측하는 용도
import serial, time # 통신 및 시간 측정용

# =========================
# 1) 설정값
# =========================
PORT = "COM6"          # 아두이노 포트
BAUD = 9600            # 통신 속도 (baud rate)

CONF_TH = 0.8         # 신뢰도 임계값 (예측 확률이 이 이상이어야 인정)(0.80~0.95 조절)
MARGIN_TH = 0.2       # top1 - top2 확률 차이 (구분이 확실해야 인정)(0.15~0.25 조절)

STABLE_SEC = 3.5       # 3.5초 동안 숫자가 변하지 않아야 '확정'
COOLDOWN_SEC = 1.0     # 최소 전송 간격 (너무 자주 보내면, 로봇이 계속 움직이므로)
STOP_ON_ZERO = True    # 0 확정 시 시스템 중단

# =========================
# 2) 모델 로드 / 시리얼 연결
# =========================
# 학습된 CNN 모델 불러오기
model = tf.keras.models.load_model("mnist_cnn.h5")

# 아두이노 시리얼 연결
ser = serial.Serial(PORT, BAUD, timeout=1)
time.sleep(2)  # Arduino reset 대기

cap = cv2.VideoCapture(0) # 웹캠 열기

# ROI를 정사각형으로 패딩하는 함수
# 숫자 붙이는 방법 : 박스 기준으로 중앙에 배치
def make_square(img: np.ndarray) -> np.ndarray:
    h, w = img.shape
    size = max(h, w)
    sq = np.zeros((size, size), dtype=np.uint8)
    y0 = (size - h) // 2
    x0 = (size - w) // 2
    sq[y0:y0+h, x0:x0+w] = img
    return sq

# ROI를 질량 중심(픽셀 평균 위치) 기준으로 중앙 정렬하는 함수
'''
흰색 픽셀(숫자 부분)의 평균 위치를 계산해서
그 평균이 이미지 중앙으로 오도록 이미지를 '평행이동' 함
=> 숫자 붙이는 방법 : 숫자 모양 자체 중심으로 중앙에 배치
'''
def center_by_mass(img: np.ndarray) -> np.ndarray:
    ys, xs = np.where(img > 0) # 숫자 픽셀 좌표 모으기
    if len(xs) == 0 or len(ys) == 0:
        return img

    # 평균 위치 구하기
    cy = int(np.mean(ys))
    cx = int(np.mean(xs))

    # 중앙으로 옮기기 위한 이동량 계산
    h, w = img.shape
    shift_y = (h // 2) - cy
    shift_x = (w // 2) - cx

    # 이미지 이동(빈곳은 검정으로 채움)
    M = np.float32([[1, 0, shift_x], [0, 1, shift_y]])
    shifted = cv2.warpAffine(img, M, (w, h), borderValue=0)
    return shifted

# =========================
# 3) "3.5초 안정성"을 위한 상태 변수들
# =========================
candidate_digit = None      # 지금 "후보로 관찰 중인 숫자"
candidate_start = 0.0       # 그 후보가 처음 관찰된 시작 시간

confirmed_digit = None      # 마지막으로 확정해서 전송한 숫자(중복 전송 방지)
last_send_time = 0.0        # 마지막 전송 시간(쿨다운용)

stopped = False             # 0 확정 시 중단 플래그

# 전처리 커널(획연결/굵게 만들 때 사용)
kernel = np.ones((3,3), np.uint8)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # ---------- (A) 영상 전처리 + ROI 추출 ----------
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 0)

    # 이진화(배경/숫자 분리)
    _, binary = cv2.threshold(
        blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )

    # morphology(끊긴 획 복원)
    # 7/8/9 특징(가로획/고리) 보존을 위해 연결/굵기 보강
    # MORPH_CLOSE : 작은 구멍 메우기 + 끊어진 획 연결
    # dilate : 흰색(숫자)을 약간 두껍게 
    binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel, iterations=1)
    binary = cv2.dilate(binary, kernel, iterations=1)

    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    vis = frame.copy()

    # 화면에 표시할 텍스트
    pred_text = "No digit"
    status_text = ""

    # 예측 결과 저장 변수
    digit = None
    conf = 0.0
    margin = 0.0  # top1-top2 차이

    if contours and not stopped:
        cnt = max(contours, key=cv2.contourArea)
        if cv2.contourArea(cnt) > 800:
            x, y, w, h = cv2.boundingRect(cnt) #숫자를 감싸는 사각형

            # ROI 잘림 방지를 위해 마진 부여
            m = 10
            x0 = max(0, x - m)
            y0 = max(0, y - m)
            x1 = min(binary.shape[1], x + w + m)
            y1 = min(binary.shape[0], y + h + m)

            cv2.rectangle(vis, (x0,y0), (x1,y1), (0,255,0), 2)

            roi = binary[y0:y1, x0:x1] # 숫자만 잘라낸 이미지 조각
            sq = make_square(roi) # 정사각형으로 패딩
            sq = center_by_mass(sq) # 질량 중심 중앙 정렬
            
            # MNIST처럼 바깥 여백을 추가 (도메인 갭 완화)
            sq = cv2.copyMakeBorder(sq, 10, 10, 10, 10, cv2.BORDER_CONSTANT, value=0)

            #28 x 28 리사이즈 + 정규화 => CNN이 요구하는 입력 형태로 변환 완료
            digit_28 = cv2.resize(sq, (28,28)) / 255.0
            digit_28 = digit_28.reshape(1,28,28,1)

            # ---------- (A-2) 예측: top2 + margin ----------
            pred = model.predict(digit_28, verbose=0)[0]  #길이 10짜리 확률 배열
            top2 = np.argsort(pred)[-2:] # 확률값을 오름차순으로 정렬 후, 상위 2개 추출
            best = int(top2[-1]) # 1등 숫자
            second = int(top2[-2]) # 2등 숫자

            conf = float(pred[best]) # 1등 확률
            margin = float(pred[best] - pred[second]) # 1등과 2등과의 확률값 차이
            digit = best # 예측 숫자

            # 화면에 표시할 문장
            pred_text = f"Predicted: {digit} (conf={conf:.2f}, margin={margin:.2f})"

            # (선택) 모델 입력 28x28 확인 창
            # preview = (digit_28.reshape(28,28) * 255).astype(np.uint8)
            # cv2.imshow("Model Input 28x28", preview)

    # ---------- (B) 3.5초 안정성 판단 로직 ----------
    now = time.time() #현재 시각(초 단위)

    if stopped: # stopped이면, 더이상 판단하지 않음
        status_text = "STOPPED (show 0 -> home). Press ESC to exit."
    else:
        # conf + margin 조건을 동시에 만족할 때만 후보로 인정
        if digit is not None and conf >= CONF_TH and margin >= MARGIN_TH:
            if candidate_digit is None or digit != candidate_digit:
                candidate_digit = digit
                candidate_start = now
        else:
            candidate_digit = None #초기화

        if candidate_digit is not None:
            stable_for = now - candidate_start # 같은 후보가 유지된 시간
            status_text = f"Candidate: {candidate_digit} stable {stable_for:.1f}s / {STABLE_SEC:.1f}s"

            if stable_for >= STABLE_SEC:
                # 같은 숫자 중복 전송 방지 + cooldown으로 너무 자주 전송 방지
                if candidate_digit != confirmed_digit and (now - last_send_time) >= COOLDOWN_SEC:
                    ser.write((str(candidate_digit) + "\n").encode()) #아두이노로 보내기
                    print(f"[SEND] {candidate_digit}")

                    confirmed_digit = candidate_digit
                    last_send_time = now

                    if STOP_ON_ZERO and candidate_digit == 0:
                        stopped = True
                        status_text = "STOPPED (0 confirmed)."
        else:
            status_text = f"Waiting stable digit (conf>={CONF_TH:.2f}, margin>={MARGIN_TH:.2f})"

    # ---------- (C) 화면 표시 ----------
    cv2.putText(vis, pred_text, (10,40),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
    cv2.putText(vis, status_text, (10,80),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255,255,255), 2)

    cv2.imshow("Digit Recognition (Stable)", vis)
    cv2.imshow("Binary", binary)

    if cv2.waitKey(1) & 0xFF == 27:  # ESC
        break

# ---------- (D) 종료 처리 ----------
cap.release()
cv2.destroyAllWindows()
ser.close()