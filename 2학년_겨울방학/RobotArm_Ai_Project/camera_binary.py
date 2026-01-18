import cv2

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("카메라를 열 수 없습니다.")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # 1. 흑백
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # 2. 블러 (노이즈 제거)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    # 3. 이진화 (자동 임계값)
    _, binary = cv2.threshold(
        blur,
        0,
        255,
        cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )

    cv2.imshow("Original", frame)
    cv2.imshow("Binary", binary)

    if cv2.waitKey(1) & 0xFF == 27:  # ESC
        break

cap.release()
cv2.destroyAllWindows()