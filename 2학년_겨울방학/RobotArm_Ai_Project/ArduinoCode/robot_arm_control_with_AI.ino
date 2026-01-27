/*
시리얼 입력(숫자 0~9)에 따라 로봇팔(서보모터 4개)을 지정된 포즈로 이동시키는 프로그램

이 코드의 목적:
- 아두이노에 연결된 4개의 서보모터(bottom, arm1, arm2, grip)를 제어
- 숫자(0~9)에 대응하는 포즈 테이블을 미리 정의해두고, 입력된 숫자에 따라 로봇팔을 해당 위치로 이동시킴
- 각도 제한을 두어 서보모터가 물리적으로 무리하지 않도록 보호
- 이동 시 부드럽게 각도를 변화시켜 자연스러운 동작을 구현
*/

#include <Servo.h>

// ===== Servo 선언 =====
Servo bottom, arm1, arm2, grip;
Servo servo[4] = {bottom, arm1, arm2, grip};

// 현재 각도 상태 (시작은 HOME 포즈)
int preVal[4] = {90, 76, 117, 7}; 

// 핀 번호
int pin[4] = {4, 5, 6, 7};

// ===== 숫자(0~9)별 포즈 테이블 =====
// 각 숫자에 대응하는 bottom, arm1, arm2, grip 각도 값
int pose[10][4] = {
  /*0*/ { 90,  76, 117,  7},  // HOME
  /*1*/ { 52,  99, 110,  7},
  /*2*/ { 66,  99, 110,  7},
  /*3*/ { 74,  99, 110,  7},
  /*4*/ { 82,  99, 110,  7},
  /*5*/ { 90,  99, 110,  7},
  /*6*/ { 102, 99, 110,  7},
  /*7*/ { 109, 99, 110,  7},
  /*8*/ { 119, 99, 110,  7},
  /*9*/ { 128, 99, 110,  7},
};

// ===== 안전 각도 제한 =====
// 각 서보모터별 허용 범위를 벗어나지 않도록 제한
int clampAngle(int idx, int ang) {
  if (idx == 0) {            // bottom
    if (ang < 50)  ang = 50;
    if (ang > 130) ang = 130;
  } else if (idx == 1) {     // arm1
    if (ang < 70)  ang = 70;
    if (ang > 120) ang = 120;
  } else if (idx == 2) {     // arm2
    if (ang < 60)  ang = 60;
    if (ang > 120) ang = 120;
  } else if (idx == 3) {     // grip
    if (ang < 5)   ang = 5;
    if (ang > 50)  ang = 50;
  }
  return ang;
}

// ===== 부드럽게 이동 =====
// 현재 위치에서 목표 위치까지 1도씩 이동하며 자연스럽게 움직임
void servoMove(int num, int target) {
  target = clampAngle(num, target); // 안전 범위 제한 적용

  // 현재 각도가 목표보다 크면 감소 방향으로 이동
  if (preVal[num] > target) {
    for (int a = preVal[num]; a > target; a--) {
      servo[num].write(a);
      delay(10);
    }
  } 
  // 현재 각도가 목표보다 작으면 증가 방향으로 이동
  else if (preVal[num] < target) {
    for (int a = preVal[num]; a < target; a++) {
      servo[num].write(a);
      delay(10);
    }
  }
  preVal[num] = target; // 최종 위치 갱신
}

// ===== 숫자에 해당하는 위치로 이동 =====
void moveToDigit(int d) {
  if (d < 0 || d > 9) return; // 유효 범위 체크

  // bottom, arm1, arm2만 이동 (grip은 고정)
  for (int j = 0; j < 3; j++) {
    servoMove(j, pose[d][j]);
    delay(20); // 관절 간 이동 간격
  }
}

// ===== setup =====
void setup() {
  Serial.begin(9600);

  for (int i = 0; i < 4; i++) {
    servo[i].attach(pin[i]); // 핀 연결
    preVal[i] = clampAngle(i, preVal[i]); // 안전 범위 적용
    servo[i].write(preVal[i]);  // 초기 위치 이동
  }

  // 시작은 HOME 포즈
  moveToDigit(0);
  Serial.println("Ready. Send digit 0~9.");
}

// ===== loop =====
void loop() {
  // 시리얼 입력이 있을 때
  if (Serial.available()) {
    char c = Serial.read(); // 입력 문자 읽기
    
    // 숫자 문자 입력일 경우
    if (c >= '0' && c <= '9') {
      int d = c - '0'; // 문자에서 정수로 변환
      Serial.print("Move to digit: ");
      Serial.println(d);
      moveToDigit(d); // 해당 숫자 포즈로 이동
    }
  }
}