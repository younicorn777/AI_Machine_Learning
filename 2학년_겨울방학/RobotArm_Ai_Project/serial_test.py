import serial
import time

# 포트 설정
ser = serial.Serial("COM7", 9600, timeout=1)
time.sleep(2)  # Arduino 리셋 대기

while True:
    digit = input("Send digit (0-9, q to quit): ")
    if digit == 'q':
        break

    ser.write((digit + "\n").encode())
    print("Sent:", digit)

ser.close()