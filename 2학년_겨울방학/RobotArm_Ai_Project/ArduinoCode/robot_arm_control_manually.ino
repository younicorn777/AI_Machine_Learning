/*
조이스틱으로 로봇팔(서보모터 4개)을 직접 제어하는 프로그램

이 코드의 목적:
- 아두이노에 연결된 4개의 서보모터(bottom, arm1, arm2, grip)를 조이스틱으로 제어
- 조이스틱 입력값을 읽어 각 서보모터의 각도를 증가/감소 시킴
- 각도 제한을 두어 서보모터가 물리적으로 무리하지 않도록 보호
*/

#include <Servo.h>
 
// 서보모터 객체 생성 
Servo bottom, arm1, arm2, grip;
Servo servo[4] = {bottom, arm1, arm2, grip};

// 각 서보모터의 초기각도 및 아두이노 핀번호  
int preVal[4] = {90, 90, 90, 5};
int pin[4] = {4, 5, 6, 7};
 
void setup() {
  // 각 서보모터를 아두이노 핀에 연결
  for (int i = 0; i < 4; i++) {
    servo[i].attach(pin[i]);
  }

  Serial.begin(9600);

  // 각 서보모터를 초기 위치로 이동
  // write : 각도 제어시 활용(단위 : degree)
  for (int i = 0; i < 4; i++) {
    servo[i].write(preVal[i]);
  }
}

// A0: bottom / A1: arm1 / A2: arm2 /A3: grip 
void loop() {
  int Val[4];
  for (int i = 0; i < 4; i++) {
    Val[i] = analogRead(14 + i); // 조이스틱 입력값 읽기(A0~A3)
 
    // 조이스틱 반대방향으로 움직이기(arm1, arm2)
    if ( i == 2 || i == 3) {
      Val[i] = 1024 - Val[i];
    }
    
    moveServo(i, Val[i]); // 해당 서보모터 제어
  }
  delay(20);
}
 
// 서보 모터 제어
void moveServo(byte num, int joyVal) {
  // 조이스틱을 한쪽 끝으로 밀었을 때
  if (joyVal > 1000) {
    preVal[num] += 1; // 각도를 1도 증가

    // 각도 제한(서보 보호)
    if (num == 0) {       // bottom
      if (preVal[num] > 130) {
        preVal[num] = 130;
      }
    }
    else if (num == 1) {  // arm1
      if (preVal[num] > 120) {
        preVal[num] = 120;
      }
    }
    else if (num == 2) {  // arm2
      if (preVal[num] > 120) {
        preVal[num] = 120;
      }
    }
    else if (num == 3) {  // grip
      if (preVal[num] > 50) {
        preVal[num] = 50;
      }
    }
  }
 
  else if (joyVal < 100) {
    preVal[num] -= 1; // 각도를 1도 감소

    // 각도 제한(서보 보호)
    if (num == 0) {       // bottom
      if (preVal[num] < 50) {
        preVal[num] = 50;
      }
    }
    else if (num == 1) {  // arm1
      if (preVal[num] < 70) {
        preVal[num] = 70;
      }
    }
    else if (num == 2) {  // arm2
      if (preVal[num] < 60) {
        preVal[num] = 60;
      }
    }
    else if (num == 3) {  // grip
      if (preVal[num] <= 5) {
        preVal[num] = 5;
      }
    }
  }
  servo[num].write(preVal[num]); // 변경된 각도로 이동(적용)
} 
