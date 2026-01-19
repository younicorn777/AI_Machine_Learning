import cv2
import numpy as np
import tensorflow as tf
import serial, time

# =========================
# 1) 설정값 (필요하면 여기만 튜닝)
# =========================
PORT = "COM6"          # 아두이노 포트
BAUD = 9600

CONF_TH = 0.85         # 신뢰도 임계값 (안정성) - 흔들리면 0.80~0.90로 조정
STABLE_SEC = 3.5       # “5초간 변함 없음” 기준
COOLDOWN_SEC = 1.0     # 너무 자주 보내지 않도록 최소 간격
STOP_ON_ZERO = True    # 0이면 중단(요구사항 그대로)

# =========================
# 2) 모델 로드 / 시리얼 연결
# =========================
model = tf.keras.models.load_model("mnist_cnn.h5")

ser = serial.Serial(PORT, BAUD, timeout=1)
time.sleep(2)  # Arduino reset 대기

cap = cv2.VideoCapture(0)

def make_square(img):
    h, w = img.shape
    size = max(h, w)
    sq = np.zeros((size, size), dtype=np.uint8)
    y0 = (size - h) // 2
    x0 = (size - w) // 2
    sq[y0:y0+h, x0:x0+w] = img
    return sq

# =========================
# 3) "5초 안정성"을 위한 상태 변수들 (여기가 핵심)
# =========================
candidate_digit = None       # 지금 “안정성 체크 중인” 숫자
candidate_start = 0.0        # 그 숫자가 유지되기 시작한 시간

confirmed_digit = None       # 마지막으로 확정/전송한 숫자(중복 전송 방지)
last_send_time = 0.0         # 마지막 전송 시간(쿨다운)

stopped = False              # 0 확정 시 중단 플래그

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # ---------- (A) 영상 전처리 + ROI 추출 ----------
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    _, binary = cv2.threshold(
        blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )

    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    vis = frame.copy()
    pred_text = "No digit"

    digit = None
    conf = 0.0

    if contours and not stopped:
        cnt = max(contours, key=cv2.contourArea)
        if cv2.contourArea(cnt) > 800:
            x, y, w, h = cv2.boundingRect(cnt)
            cv2.rectangle(vis, (x,y), (x+w,y+h), (0,255,0), 2)

            roi = binary[y:y+h, x:x+w]
            sq = make_square(roi)
            digit_28 = cv2.resize(sq, (28,28)) / 255.0
            digit_28 = digit_28.reshape(1,28,28,1)

            pred = model.predict(digit_28, verbose=0)
            digit = int(np.argmax(pred))
            conf = float(np.max(pred))

            pred_text = f"Predicted: {digit} ({conf:.2f})"

    # ---------- (B) 여기부터가 네가 요청한 “5초 안정성 판단” 로직 ----------
    now = time.time()

    if stopped:
        # 중단 상태에서는 더 이상 판단/전송하지 않음
        status_text = "STOPPED (show 0 -> home). Press ESC to exit."
    else:
        # 1) 신뢰도 통과한 경우에만 안정성 체크
        if digit is not None and conf >= CONF_TH:
            if candidate_digit is None or digit != candidate_digit:
                # 후보 숫자가 바뀌면 타이머 리셋
                candidate_digit = digit
                candidate_start = now
            else:
                # 같은 후보 숫자가 유지 중
                pass
        else:
            # 신뢰도 미달 또는 숫자 없음 -> 후보 초기화
            candidate_digit = None

        # 2) 후보가 STABLE_SEC 이상 유지되면 "확신"
        if candidate_digit is not None:
            stable_for = now - candidate_start
            status_text = f"Candidate: {candidate_digit} stable {stable_for:.1f}s / {STABLE_SEC:.0f}s"

            if stable_for >= STABLE_SEC:
                # 3) 이미 같은 숫자를 확정했으면 다시 보내지 않음
                #    + 너무 자주 보내지 않도록 cooldown 적용
                if candidate_digit != confirmed_digit and (now - last_send_time) >= COOLDOWN_SEC:
                    # Arduino로 숫자 전송
                    ser.write((str(candidate_digit) + "\n").encode())
                    print(f"[SEND] {candidate_digit}")

                    confirmed_digit = candidate_digit
                    last_send_time = now

                    # 4) 0이면 홈 복귀 후 중단
                    if STOP_ON_ZERO and candidate_digit == 0:
                        stopped = True
                        status_text = "STOPPED (0 confirmed)."

                # 확정 후에도 계속 같은 숫자를 보여주면 계속 확정 상태이므로 후보 유지 OK
        else:
            status_text = f"Waiting stable digit (conf>={CONF_TH:.2f})"

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