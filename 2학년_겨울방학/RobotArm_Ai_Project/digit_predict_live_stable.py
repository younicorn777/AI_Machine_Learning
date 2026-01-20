import cv2
import numpy as np
import tensorflow as tf
import serial, time

# =========================
# 1) 설정값 (필요하면 여기만 튜닝)
# =========================
PORT = "COM6"          # 아두이노 포트
BAUD = 9600

CONF_TH = 0.9         # 신뢰도 임계값 (0.80~0.95 조절)
MARGIN_TH = 0.2       # top1 - top2 확률 차이 (0.15~0.25 조절 추천)

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

def make_square(img: np.ndarray) -> np.ndarray:
    """ROI를 정사각형으로 패딩하여 중앙정렬에 유리하게 만듦"""
    h, w = img.shape
    size = max(h, w)
    sq = np.zeros((size, size), dtype=np.uint8)
    y0 = (size - h) // 2
    x0 = (size - w) // 2
    sq[y0:y0+h, x0:x0+w] = img
    return sq

def center_by_mass(img: np.ndarray) -> np.ndarray:
    # img: binary (0/255), foreground=255
    ys, xs = np.where(img > 0)
    if len(xs) == 0 or len(ys) == 0:
        return img

    cy = int(np.mean(ys))
    cx = int(np.mean(xs))

    h, w = img.shape
    shift_y = (h // 2) - cy
    shift_x = (w // 2) - cx

    M = np.float32([[1, 0, shift_x], [0, 1, shift_y]])
    shifted = cv2.warpAffine(img, M, (w, h), borderValue=0)
    return shifted

# =========================
# 3) "5초 안정성"을 위한 상태 변수들
# =========================
candidate_digit = None      # 안정성 체크 중인 숫자
candidate_start = 0.0       # 그 숫자가 유지되기 시작한 시간

confirmed_digit = None      # 마지막으로 확정/전송한 숫자(중복 전송 방지)
last_send_time = 0.0        # 마지막 전송 시간(쿨다운)

stopped = False             # 0 확정 시 중단 플래그

# (선택) 전처리 커널
kernel = np.ones((3,3), np.uint8)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # ---------- (A) 영상 전처리 + ROI 추출 ----------
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 0)

    # Otsu 이진화
    _, binary = cv2.threshold(
        blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )

    # ✅ 7/8/9 특징(가로획/고리) 보존을 위해 연결/굵기 보강
    binary = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel, iterations=1)
    binary = cv2.dilate(binary, kernel, iterations=1)

    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    vis = frame.copy()
    pred_text = "No digit"
    status_text = ""

    digit = None
    conf = 0.0
    margin = 0.0  # ✅ top1-top2 차이

    if contours and not stopped:
        cnt = max(contours, key=cv2.contourArea)
        if cv2.contourArea(cnt) > 800:
            x, y, w, h = cv2.boundingRect(cnt)

            # ✅ ROI 잘림 방지를 위해 마진 부여
            m = 10
            x0 = max(0, x - m)
            y0 = max(0, y - m)
            x1 = min(binary.shape[1], x + w + m)
            y1 = min(binary.shape[0], y + h + m)

            cv2.rectangle(vis, (x0,y0), (x1,y1), (0,255,0), 2)

            roi = binary[y0:y1, x0:x1]
            sq = make_square(roi)
            sq = center_by_mass(sq)
            # ✅ MNIST처럼 여백을 조금 주기 (도메인 갭 완화)
            sq = cv2.copyMakeBorder(sq, 10, 10, 10, 10, cv2.BORDER_CONSTANT, value=0)

            digit_28 = cv2.resize(sq, (28,28)) / 255.0
            digit_28 = digit_28.reshape(1,28,28,1)

            # ---------- (A-2) 예측: top2 + margin ----------
            pred = model.predict(digit_28, verbose=0)[0]  # (10,)
            top2 = np.argsort(pred)[-2:]
            best = int(top2[-1])
            second = int(top2[-2])

            conf = float(pred[best])
            margin = float(pred[best] - pred[second])
            digit = best

            pred_text = f"Predicted: {digit} (conf={conf:.2f}, margin={margin:.2f})"

            # (선택) 모델 입력 28x28 확인 창
            # preview = (digit_28.reshape(28,28) * 255).astype(np.uint8)
            # cv2.imshow("Model Input 28x28", preview)

    # ---------- (B) 5초 안정성 판단 로직 ----------
    now = time.time()

    if stopped:
        status_text = "STOPPED (show 0 -> home). Press ESC to exit."
    else:
        # ✅ conf + margin 조건을 동시에 만족할 때만 후보로 인정
        if digit is not None and conf >= CONF_TH and margin >= MARGIN_TH:
            if candidate_digit is None or digit != candidate_digit:
                candidate_digit = digit
                candidate_start = now
        else:
            candidate_digit = None

        if candidate_digit is not None:
            stable_for = now - candidate_start
            status_text = f"Candidate: {candidate_digit} stable {stable_for:.1f}s / {STABLE_SEC:.1f}s"

            if stable_for >= STABLE_SEC:
                if candidate_digit != confirmed_digit and (now - last_send_time) >= COOLDOWN_SEC:
                    ser.write((str(candidate_digit) + "\n").encode())
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