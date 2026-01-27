# 🤖 Arduino Control Codes for Robotic Arm

---

## 🇰🇷 폴더 설명 (Korean Summary)

이 폴더는 로봇팔 제어를 위해 작성한 Arduino 코드들을 
단계별로 정리한 것입니다.  
수동 제어 → 위치 캘리브레이션 → AI 기반 자동 제어 순서로 개발되었으며,  
각 파일은 로봇팔 제어 방식의 발전 과정을 보여줍니다.  
최종적으로는 Python 기반 CNN 숫자 인식 결과를 받아  
로봇팔이 해당 숫자를 가리키도록 제어했습니다.

---

## 📌 Overview

This folder contains Arduino source codes used to control a 4-DOF robotic arm.
The codes are organized according to the development stages, starting from
manual control and calibration to AI-driven autonomous control.

Each script represents a specific role in the system and was developed
incrementally to ensure stable operation and clear debugging.

---

## 📂 File Descriptions

### 1️⃣ `robot_arm_control_manually.ino`

**Purpose**
- Manual control of the robotic arm using two joysticks
- Direct servo angle adjustment

**Key Features**
- Individual control of base, shoulder, elbow, and gripper
- Angle limits applied to protect servos
- Used to understand mechanical range and movement behavior

**Role in Project**
- Initial testing of robotic arm hardware
- Verification of servo motor functionality and wiring

---

### 2️⃣ `robot_arm_configPos.ino`

**Purpose**
- Calibration of predefined arm positions
- Recording servo angles for specific target points

**Key Features**
- Stores multiple servo angle sets
- Allows replaying saved motion sequences
- Used to map digits (0–9) to corresponding arm pointing positions

**Role in Project**
- Establishes a lookup table between recognized digits and arm poses
- Bridges the gap between perception (AI) and actuation (robot arm)

---

### 3️⃣ `robot_arm_control_with_AI.ino` ⭐

**Purpose**
- Automatic robotic arm control based on AI prediction results
- Receives digit information from Python via serial communication

**Key Features**
- Serial communication with Python (CNN inference)
- Digit-based position selection
- Moves robotic arm to point at the recognized digit
- Returns to home position when digit `0` is received

**Role in Project**
- Final integrated control code
- Connects AI inference results to physical robot motion

---

## 🔧 Hardware Configuration

- Micro servo motors (4 DOF)
- Arduino board
- External power supply for servos
- Serial communication with PC (USB)

---

## 🎯 Design Philosophy

- Start simple: manual control before automation
- Calibrate physical positions before AI integration
- Separate perception (AI) and actuation (Arduino)
- Prioritize stability and reproducibility for live demonstrations

---

## 📝 Note

These Arduino codes are designed to work in conjunction with the Python-based
digit recognition system located in the main project directory.
The final demonstration uses `robot_arm_control_with_AI.ino`.