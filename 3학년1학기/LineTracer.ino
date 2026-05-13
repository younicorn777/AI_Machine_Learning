int RightMotor_E_pin = 5; int LeftMotor_E_pin = 6;
int RightMotor_1_pin = 8; int RightMotor_2_pin = 9;
int LeftMotor_3_pin = 10; int LeftMotor_4_pin = 11;

int L_Line = A5; int C_Line = A4; int R_Line = A3;

/*
건전지:
speed_max = 200; 
speed_turn_outer = 160; // 150(실패)
int speed_turn_inner = 180; // 170(실패) 

축전지:
speed_max = 240(성공); 
speed_turn_outer = 170(성공); 
int speed_turn_inner = 190(성공); 
*/


// 상태 변수
int speed_max = 200; 
int speed_turn_outer = 155; 
int speed_turn_inner = 175; 
int diff = 20; // 오른쪽 모터가 20 더 빠르므로 빼줄 값

void setup() {
  pinMode(RightMotor_E_pin, OUTPUT);
  pinMode(LeftMotor_E_pin, OUTPUT);
  pinMode(RightMotor_1_pin, OUTPUT);
  pinMode(RightMotor_2_pin, OUTPUT);
  pinMode(LeftMotor_3_pin, OUTPUT);
  pinMode(LeftMotor_4_pin, OUTPUT);
}

void loop() {
  int L = digitalRead(L_Line);
  int C = digitalRead(C_Line);
  int R = digitalRead(R_Line);

  // 1. 직진 (가운데 검은선)
  if (L == 0 && C == 1 && R == 0) {
    digitalWrite(LeftMotor_3_pin, 1);  digitalWrite(LeftMotor_4_pin, 0);
    digitalWrite(RightMotor_1_pin, 1); digitalWrite(RightMotor_2_pin, 0);
    analogWrite(LeftMotor_E_pin, speed_max);
    analogWrite(RightMotor_E_pin, speed_max - diff); // 오른쪽 속도 다운
  }
  
  // 2. 우회전 (오른쪽 검은선 감지)
  else if (L == 0 && C == 0 && R == 1) {
    digitalWrite(LeftMotor_3_pin, 1);  digitalWrite(LeftMotor_4_pin, 0);
    digitalWrite(RightMotor_1_pin, 0); digitalWrite(RightMotor_2_pin, 1);
    analogWrite(LeftMotor_E_pin, speed_turn_outer);
    analogWrite(RightMotor_E_pin, speed_turn_inner - diff); // 역회전도 동일하게 보정
  }
  
  // 3. 좌회전 (왼쪽 검은선 감지)
  else if (L == 1 && C == 0 && R == 0) {
    digitalWrite(LeftMotor_3_pin, 0);  digitalWrite(LeftMotor_4_pin, 1);
    digitalWrite(RightMotor_1_pin, 1); digitalWrite(RightMotor_2_pin, 0);
    analogWrite(LeftMotor_E_pin, speed_turn_inner);
    analogWrite(RightMotor_E_pin, speed_turn_outer - diff); // 바깥쪽 돌 때도 보정
  }
}
