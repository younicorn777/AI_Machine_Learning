'''
camera_binary의 Docstring

웹캠 영상 전처리 파이프라인

- 전처리 단계:
  1. 흑백 변환 (Grayscale): 색상 정보를 제거하고 숫자의 모양(선, 획, 구조)에 집중
     → 연산량 감소, 조명 변화에 덜 민감
  2. 블러 처리 (Gaussian Blur): 작은 노이즈 제거, 숫자 윤곽을 부드럽게
     → 인식률 향상
  3. 이진화 (Thresholding + Otsu): 숫자와 배경을 명확히 구분
     → 숫자는 흰색, 배경은 검정으로 단순화
- 최종적으로 원본 영상과 이진화된 영상을 동시에 출력한다.
'''

import cv2

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("카메라를 열 수 없습니다.")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # 1. 흑백 변환
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # 2. 블러 (노이즈 제거)
    # 작은 잡음이나 글씨 주변의 거친 픽셀을 부드럽게 만듦
    # → 숫자 인식 시 불필요한 노이즈를 줄여 정확도 향상
    blur = cv2.GaussianBlur(gray, (5, 5), 0)

    # 3. 이진화 (자동 임계값) : 흑 또는 백
    '''
    반환값 : _, binary
    첫번째 반환값은 Otsu가 계산한 실제 임계값인데, 
    우리는 쓰지 않으므로 _로 버림
    '''
    _, binary = cv2.threshold(
        blur,              # 입력 영상
        0,                 # 기준 임계값 :  Otsu 알고리즘이 자동 결정(0은 의미 없음)
        255,               # 기준을 넘는 픽셀에 적용할 값: 픽셀을 흰색으로 설정
        cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU # 이진화 반대 + 오츠 알고리즘 사용
    )
    # THRESH_BINARY_INV: 글씨 부분을 흰색, 배경을 검은색으로 반전
    # Otsu 알고리즘: 영상의 히스토그램을 분석해 최적의 임계값을 자동으로 선택
    # → 손글씨 숫자를 더 뚜렷하게 분리

    cv2.imshow("Original", frame)
    cv2.imshow("Binary", binary)

    if cv2.waitKey(1) & 0xFF == 27:  # ESC
        break

cap.release()
cv2.destroyAllWindows()