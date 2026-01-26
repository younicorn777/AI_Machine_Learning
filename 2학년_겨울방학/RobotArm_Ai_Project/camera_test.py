'''
camera_test의 Docstring

카메라 테스트
'''

# 0. OpenCV 라이브러리를 불러오기
import cv2

# 1. 카메라 열기
# VideoCapture 객체를 생성
# 인자 '0'은 기본 웹캠을 의미
cap = cv2.VideoCapture(0)  

# 카메라를 열 수 없는 경우
# cap.isOpened()는 카메라가 정상적으로 열렸는지 확인
# 열리지 않았다면 메시지를 출력하고 프로그램 종료
if not cap.isOpened():  
    print("카메라를 열 수 없습니다.")  
    exit()  # 프로그램 종료

# 카메라를 열 수 있는 경우
# 2. 무한 루프: 카메라에서 프레임을 계속 읽어오기
# => 효과 : 실시간으로 영상을 받아옴
while True:
    ret, frame = cap.read()  
    # ret: 프레임을 성공적으로 읽었는지 여부 (True/False)
    # frame: 읽어온 실제 영상 데이터 (이미지 배열)

    # 프레임을 읽지 못했다면 루프 종료 => 시스템 종료
    if not ret:  
        break 

    # 읽어온 프레임을 화면에 출력(frame)
    # 창 제목은 "Camera Test - ESC to exit" 
    cv2.imshow("Camera Test - ESC to exit", frame)  

    # 카메라 테스트 종료 : ESC 버튼 누르기
    # waitKey(1): 키 입력을 1ms 동안 기다림.
    # => 정리 : 1ms 동안 ESC 입력이 없으면, 다음 루프로 넘어가 새로운 프레임 띄움
    if cv2.waitKey(1) & 0xFF == 27:  # ESC 키 입력 확인
        break  

# 3. 카메라와 창 닫기
cap.release() # 카메라 연결 해제 (독점 해제) 
cv2.destroyAllWindows() # OpenCV에서 생성한 모든 창을 닫음(리소스 정리)