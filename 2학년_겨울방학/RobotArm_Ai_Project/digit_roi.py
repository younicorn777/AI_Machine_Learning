'''
digit_roi의 Docstring

ROI : Region Of Interest (관심영역)
웹캠 영상에서 손글씨 숫자를 추출하여 MNIST 입력 형태(28x28)로 변환하는 프로그램

이 코드의 목적:
- 웹캠으로 입력된 실시간 영상에서 손글씨 숫자를 인식하기 위한 전처리 과정을 수행
- 주요 단계:
  1. Grayscale 변환 → Blur → Binary (숫자는 흰색, 배경은 검정)
     - 색상 제거, 노이즈 감소, 숫자와 배경을 명확히 구분
  2. Contour 탐색 → 가장 큰 외곽선 선택 (숫자라고 가정)
     - 작은 잡음은 무시
  3. ROI 추출 → 정사각형 패딩 → 28x28 크기로 리사이즈
     - CNN(MNIST 학습 모델) 입력과 동일한 형태로 변환
  4. 결과 시각화
     - 원본 영상 + 바운딩 박스
     - 이진화 영상
     - ROI (잘라낸 숫자)
     - MNIST 형태로 변환된 숫자 (확대 표시)
'''

import cv2
import numpy as np

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("카메라를 열 수 없습니다.")
    exit()

"""
make_square 함수  

입력: binary ROI (숫자는 흰색, 배경은 검정)
출력: 정사각형 형태로 패딩된 이미지
이유: 
MNIST는 항상 정사각형(28×28)이므로, 
직사각형 숫자 이미지를 중앙에 배치하고 
여백을 검정으로 채워 맞춰줌
"""
def make_square(img: np.ndarray) -> np.ndarray:
    h, w = img.shape
    size = max(h, w) # 가장 긴 변 기준으로 정사각형 크기 결정
    sq = np.zeros((size, size), dtype=np.uint8) # 검정 배경 생성(모든 배열 값이 0)
    
    # 숫자를 정중앙에 배치하기 위한 여백 계산
    y0 = (size - h) // 2
    x0 = (size - w) // 2

    # 검은 도화지(sq)의 계산된 좌표(y0, x0) 위치에 실제 숫자 이미지(img)를 덮어쓰기
    sq[y0:y0+h, x0:x0+w] = img
    return sq # 결론 : 검은 도화지 중앙에 숫자를 붙여 반환

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # 1) Grayscale -> blur -> binary (white digit on black)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY) # 컬러 → 흑백
    blur = cv2.GaussianBlur(gray, (5, 5), 0) # 노이즈 제거
    _, binary = cv2.threshold(
        blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )

    # 2) Contour 탐색 (외곽선만)
    # RETR_EXTERNAL: 가장 바깥쪽 윤곽선만 추출 (내부 작은 윤곽선 무시)
    # CHAIN_APPROX_SIMPLE: 윤곽선 좌표를 단순화하여 저장(끝점만 저장)
    # contours 반환값 : 이미지에서 발견된 모든 외곽선들의 정보가 담겨 있음
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    vis = frame.copy()  # 원본 복사 (시각화용)
    roi_view = np.zeros((200, 200), dtype=np.uint8)     # ROI 표시용
    mnist_view = np.zeros((280, 280), dtype=np.uint8)   # MNIST 28x28 확대 표시용

    # 숫자로 볼만한 잡음이 있을 때
    if contours:
        cnt = max(contours, key=cv2.contourArea) # 가장 큰 윤곽선 선택(여러 잡음 중 실제 숫자 부분일 가능성이 높은 잡음)
        area = cv2.contourArea(cnt) # 가장 큰 윤곽선의 면적

        # 너무 작은 잡음은 무시 (상황에 따라 조절)
        if area > 800:
            # 1) 바운딩
            # 바운딩 박스(Bounding Box): 객체(숫자)의 위치와 크기를 나타내는 최소 직사각형
            # 바운딩 목적: 숫자 영역을 표시하고 ROI를 추출하기 위한 좌표 정보 제공
            x, y, w, h = cv2.boundingRect(cnt) # 바운딩 박스 좌표(박스 왼쪽 상단 좌표), 너비, 높이

            # 2) 원본에 박스 표시 : "지금 이 숫자를 보고 있다"는 것을 사용자에게 시각적으로 보여줌
            cv2.rectangle(vis, (x, y), (x+w, y+h), (0, 255, 0), 2)

            # 3) ROI 추출 : 숫자가 있는 사각형 영역만 추출 (배열값)
            roi = binary[y:y+h, x:x+w]

            # 4) 정사각형 패딩 + 28 x 28 크기로 재조정
            # INTER_AREA : 이미지 축소 시, 주변 픽셀들의 평균을 내서 줄임 -> 숫자가 끊어지지 않고 유지됨
            sq = make_square(roi)
            digit_28 = cv2.resize(sq, (28, 28), interpolation=cv2.INTER_AREA)

            '''
            모니터링용 확대

            * 28 x 28은 너무 작아서 사람이 확인하기 어려움 
            -> 다시 큰 사이즈로 확대해서 보여줌. 
            *INTER_NEAREST: 확대할 때 픽셀을 부드럽게 뭉개지 않고, 원래 픽셀 형태를 그대로 유지(계단 현상 유지)해서 보여줌.
            -> AI가 보는 실제 픽셀 상태를 확인하기에 좋습니다.
            '''
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