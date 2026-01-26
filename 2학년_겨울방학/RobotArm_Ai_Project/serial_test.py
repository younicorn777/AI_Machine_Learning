'''
serial_test의 Docstring

코드 간단 설명 :
Python에서 COM7 포트를 통해 Arduino와 연결하고, 
사용자가 입력한 숫자를 시리얼 통신으로 보내는 간단한 테스트 프로그램
'''

import serial   # PySerial 라이브러리 불러오기 (시리얼 통신을 위한 모듈)
import time     # 시간 지연을 주기 위한 모듈

# 포트 설정
ser = serial.Serial("COM7", 9600, timeout=1)
# "COM7" : 연결된 장치(예: Arduino)가 사용하는 포트 번호
# 9600   : 통신 속도, Arduino 코드에서도 동일하게 맞춰야 함
# timeout=1 : 데이터 수신 시 최대 1초까지 대기

'''
* Arduino가 연결 직후 자동 리셋되므로 준비될 때까지 2초 대기*
만약 바로 데이터를 보내면, Arduino가 아직 초기화 중이라서
데이터를 제대로 받지 못할 수 있음. 
따라서 Arduino가 부팅을 끝내고 
준비된 상태에서 데이터를 받을 수 있도록 함.
'''

time.sleep(2)

# 무한 루프: 사용자 입력을 받아서 Arduino로 전송
while True:
    # 사용자로부터 숫자(0~9) 또는 'q' 입력 받기
    digit = input("Send digit (0-9, q to quit): ")

    if digit == 'q':
        break  # 'q' 입력 시 루프 종료

    ser.write((digit + "\n").encode())
    # 입력한 숫자를 문자열로 만든 뒤, 줄바꿈("\n")을 붙여서 전송
    # .encode() : 문자열을 바이트 데이터로 변환 (시리얼 통신은 바이트 단위로 전송됨)

    print("Sent:", digit)
    # 전송한 데이터를 콘솔에 출력 (확인용)

# 루프 종료 후 포트 닫기
ser.close()
# 시리얼 포트를 닫아 자원 해제 (다른 프로그램이 포트를 사용할 수 있도록 반납)