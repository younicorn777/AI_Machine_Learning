import cv2
import numpy as np
import tensorflow as tf
import serial, time

# 모델 로드
model = tf.keras.models.load_model("mnist_cnn.h5")

# 시리얼 설정
ser = serial.Serial("COM7", 9600, timeout=1)
time.sleep(2)
last_sent = -1
last_time = 0

cap = cv2.VideoCapture(0)

def make_square(img):
    h, w = img.shape
    size = max(h, w)
    sq = np.zeros((size, size), dtype=np.uint8)
    y0 = (size - h) // 2
    x0 = (size - w) // 2
    sq[y0:y0+h, x0:x0+w] = img
    return sq

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    _, binary = cv2.threshold(
        blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )

    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    vis = frame.copy()
    pred_text = "No digit"

    if contours:
        cnt = max(contours, key=cv2.contourArea)
        if cv2.contourArea(cnt) > 800:
            x, y, w, h = cv2.boundingRect(cnt)
            cv2.rectangle(vis, (x,y), (x+w,y+h), (0,255,0), 2)

            roi = binary[y:y+h, x:x+w]
            sq = make_square(roi)
            digit_28 = cv2.resize(sq, (28,28)) / 255.0
            digit_28 = digit_28.reshape(1,28,28,1)

            pred = model.predict(digit_28, verbose=0)
            digit = np.argmax(pred)
            conf = np.max(pred)

            pred_text = f"Predicted: {digit} ({conf:.2f})"

            now = time.time()
            if conf > 0.90 and digit != last_sent and now - last_time > 1.0:
                ser.write((str(digit) + "\n").encode())
                print(f"Sent to Arduino: {digit}")
                last_sent = digit
                last_time = now

    cv2.putText(
        vis, pred_text, (10,40),
        cv2.FONT_HERSHEY_SIMPLEX, 1,
        (0,255,0), 2
    )

    cv2.imshow("Digit Recognition", vis)
    cv2.imshow("Binary", binary)

    if cv2.waitKey(1) & 0xFF == 27:
        break

ser.close()
cap.release()
cv2.destroyAllWindows()