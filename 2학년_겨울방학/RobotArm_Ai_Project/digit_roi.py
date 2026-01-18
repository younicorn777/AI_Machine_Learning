import cv2
import numpy as np

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("카메라를 열 수 없습니다.")
    exit()

def make_square(img: np.ndarray) -> np.ndarray:
    """img: binary ROI (white digit on black). Return squared image with padding."""
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

    # 1) Grayscale -> blur -> binary (white digit on black)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, binary = cv2.threshold(
        blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )

    # 2) Find contours (external only)
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    vis = frame.copy()
    roi_view = np.zeros((200, 200), dtype=np.uint8)
    mnist_view = np.zeros((280, 280), dtype=np.uint8)  # show 28x28 enlarged

    if contours:
        # pick largest contour (assumes single digit shown)
        cnt = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(cnt)

        # 너무 작은 잡음은 무시 (상황에 따라 조절)
        if area > 800:
            x, y, w, h = cv2.boundingRect(cnt)

            # draw bbox
            cv2.rectangle(vis, (x, y), (x+w, y+h), (0, 255, 0), 2)

            # crop ROI from binary image
            roi = binary[y:y+h, x:x+w]

            # square pad + resize to 28x28
            sq = make_square(roi)
            digit_28 = cv2.resize(sq, (28, 28), interpolation=cv2.INTER_AREA)

            # 보기 좋게 크게 확대
            roi_view = cv2.resize(roi, (200, 200), interpolation=cv2.INTER_NEAREST)
            mnist_view = cv2.resize(digit_28, (280, 280), interpolation=cv2.INTER_NEAREST)

    cv2.imshow("1) Original + bbox", vis)
    cv2.imshow("2) Binary", binary)
    cv2.imshow("3) ROI (cropped)", roi_view)
    cv2.imshow("4) MNIST-like 28x28 (zoomed)", mnist_view)

    if cv2.waitKey(1) & 0xFF == 27:  # ESC
        break

cap.release()
cv2.destroyAllWindows()