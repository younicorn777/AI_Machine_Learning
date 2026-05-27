int RightMotor_E_pin = 5;
int LeftMotor_E_pin = 6;
int RightMotor_1_pin = 8;
int RightMotor_2_pin = 9;
int LeftMotor_3_pin = 10;
int LeftMotor_4_pin = 11;

int L_Line = A5;
int C_Line = A4;
int R_Line = A3;

int L_MotorSpeed = 210; // 230, 210(최근 잘 되던 속도), 205(0527: 회전34와 잘 되던 속도) ,210(36)
int R_MotorSpeed = 190; // 210, 190(최근 잘 되던 속도), 185(0527: 회전34와 잘 되던 속도),190(34)

int SL = 1;
int SC = 1;
int SR = 1;

unsigned long startTime = 0; 
bool isBoosterActive = true; 

void setup() {
  pinMode(RightMotor_E_pin, OUTPUT);
  pinMode(LeftMotor_E_pin, OUTPUT);
  pinMode(RightMotor_1_pin, OUTPUT);
  pinMode(RightMotor_2_pin, OUTPUT);
  pinMode(LeftMotor_3_pin, OUTPUT);
  pinMode(LeftMotor_4_pin, OUTPUT);
  
  startTime = millis(); 
}

void loop() {
  int L = digitalRead(L_Line);
  int C = digitalRead(C_Line);
  int R = digitalRead(R_Line);

  int currentL_Speed = L_MotorSpeed;
  int currentR_Speed = R_MotorSpeed;

  
  if (isBoosterActive) {
    if (millis() - startTime < 1500) {
      currentL_Speed = 250; // 250일때 안정적
      currentR_Speed = 250; // 250일때 안정적
    } else {
      isBoosterActive = false; 
    }
  }
  
  
  if ( L == LOW && C == HIGH && R == LOW ) {
    motor_control(1, 1, currentR_Speed, currentL_Speed); 
  }
  else if (L == LOW && R == HIGH ){
    motor_control(-1, 1, currentR_Speed + 36, currentL_Speed);  // +33, 34(가장 좋은 속도),36
  }
  else if (L == HIGH && R == LOW ) {
    motor_control(1, -1, currentR_Speed, currentL_Speed + 34);   // +33, 32(가장 좋은 속도),34
  }
  

}

void motor_control(int R_dir, int L_dir, int R_speed, int L_speed) {
  digitalWrite(RightMotor_1_pin, R_dir == 1 ? HIGH : LOW);
  digitalWrite(RightMotor_2_pin, R_dir == 1 ? LOW : HIGH);
  digitalWrite(LeftMotor_3_pin, L_dir == 1 ? HIGH : LOW);
  digitalWrite(LeftMotor_4_pin, L_dir == 1 ? LOW : HIGH);

  analogWrite(RightMotor_E_pin, constrain(R_speed, 0, 255));
  analogWrite(LeftMotor_E_pin, constrain(L_speed, 0, 255));
}
