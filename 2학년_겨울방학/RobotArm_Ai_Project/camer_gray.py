'''
camer_gray의 Docstring

흑백 변환을 한 이유 :
손글씨 숫자 인식에서는 색깔이 중요하지 않고, 
숫자의 모양(선, 획, 구조)이 중요
=> 연산량과 조명의 영향을 줄이기 위해 변환함
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