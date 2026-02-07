import cv2

# 웹캠 열기 (0번: 노트북 기본 카메라)
cap = cv2.VideoCapture(0)

# 카메라가 열리지 않으면 종료
if not cap.isOpened():
    print("카메라를 열 수 없습니다.")
    exit()

print("카메라 연결 성공. ESC 키를 누르면 종료됩니다.")

while True:
    ret, frame = cap.read()

    if not ret:
        print("프레임을 읽을 수 없습니다.")
        break

    cv2.imshow("Camera Test", frame)

    # ESC 키(27) 누르면 종료
    if cv2.waitKey(1) & 0xFF == 27:
        print("종료합니다.")
        break

# 자원 해제
cap.release()
cv2.destroyAllWindows()