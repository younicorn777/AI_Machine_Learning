'''
camer_gray의 Docstring

웹캠 영상 흑백 변환 비교 프로그램

이 코드의 목적:
- 웹캠으로 입력된 실시간 영상을 받아서 컬러 영상과 흑백 영상(Grayscale)을 동시에 출력
- 흑백 변환을 하는 이유:
  1. 손글씨 숫자 인식과 같은 영상 처리에서는 색상보다 모양(선, 획, 구조)이 중요
  2. 색상 정보를 제거하면 연산량이 줄고, 조명 변화에 덜 민감해짐
- 따라서 원본과 흑백 영상을 나란히 출력하여 차이를 직관적으로 확인할 수 있음

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

    # 흑백 변환
    # frame은 기본적으로 BGR(Blue, Green, Red) 컬러 형식
    # COLOR_BGR2GRAY 옵션을 사용하면 흑백(Grayscale) 영상으로 변환됨
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # 원본과 변환된 결과를 동시에 출력하여 비교
    cv2.imshow("Original", frame)
    cv2.imshow("Grayscale", gray)

    if cv2.waitKey(1) & 0xFF == 27:  # ESC
        break

cap.release()
cv2.destroyAllWindows()