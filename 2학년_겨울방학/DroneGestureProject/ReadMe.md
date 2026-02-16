# 🚁 Gesture-Based Drone Control System

---

## 🇰🇷 프로젝트 요약 (Korean Summary)

본 프로젝트는 웹캠 영상에서 손 제스처를 인식하고,  
손가락 개수를 숫자로 변환하여 드론의 물리적 동작(이륙, 이동, 착륙)으로 연결하는 시스템입니다.  

MediaPipe 기반 손 랜드마크 인식과 CoDrone Mini의 라이브러리를 활용하여  
실시간 비전 인식 → 안정성 판단 → 하드웨어 제어까지 전체 흐름을 구현하였습니다.  

단순 제스처 인식 구현을 넘어서,  
실제 비행 실험을 통해 발생한 문제를 해결하는 과정에 중점을 둔 프로젝트입니다.

---

## 📌 Project Overview

This project implements a real-time gesture recognition system  
that controls a drone using hand gestures detected from a webcam.

Hand landmarks are extracted using MediaPipe,  
and the number of extended fingers (0–5) is mapped to drone commands.

Rather than focusing only on gesture recognition,  
this project emphasizes:

- **system-level integration**
- motion stability
- hardware-aware control tuning
- safe initialization and execution logic

---

## 🧠 Gesture Recognition Pipeline

The system processes the camera input as follows:

### 🔄 Overall Pipeline

Camera → Hand Landmark Detection → Finger Counting  
→ Stable Gesture Confirmation → Drone Mission Execution

---

### 1. Camera Input (OpenCV)

- Captures real-time webcam frames  
- Converts BGR to RGB for MediaPipe processing  

---

### 2. Hand Landmark Detection (MediaPipe)

- Detects 21 hand landmarks  
- Tracks hand movement in real-time  
- Supports dynamic gesture recognition  

---

### 3. Finger Counting Logic

- Index / Middle / Ring / Pinky  
  → Compare fingertip y-coordinate with lower joint  

- Thumb  
  → Distance-based comparison between thumb tip and pinky base  
  → Improves robustness against palm/back orientation differences  

---

### 4. Stability Confirmation

To avoid unintended drone motion:

- The same gesture must be maintained for **1 second**
- After execution, the hand must be lowered before the next command
- Edge-trigger structure prevents repeated execution

This significantly improves real-world safety and control reliability.

---

## 🚁 Drone Motion Control Design

Real-world flight testing revealed several control challenges.

To improve motion stability, the following structure was implemented:

### 🔧 Control Structure

- `control()` → raw directional control  
- `brake()` → short reverse thrust to remove inertia  
- `hover()` → trim-based stabilization  

### 🔄 Movement Pattern

Move → Brake → Hover

This pattern reduces drift and overshoot after movement.

---

## 🔧 Experimental Findings & Improvements

### 1️⃣ Hover Instability

- Problem: Drone drifted during hover  
- Solution: Applied trim values only in hover phase  

---

### 2️⃣ Inertia After Movement

- Problem: Drone continued moving after control input ended  
- Solution: Introduced brake phase before hover  

---

### 3️⃣ Unexpected Restart Behavior

- Problem: After collision or disconnection, previous motion resumed  
- Solution: Implemented `safe_initialize()` routine  
  - Repeated landing commands  
  - Control value reset  

---

### 4️⃣ Inconsistent Movement Distance

- Identical control values produced different results  
- Cause: Real-time battery drain affects motor power  
- Limitation: No API access to real-time battery compensation  

---

## 🎮 Gesture-to-Drone Mapping

| Gesture | Action |
|----------|--------|
| 1 | Takeoff |
| 2 | Forward |
| 3 | Backward |
| 4 | Left |
| 5 | Right |
| 0 | Landing |

---

## 🔧 Implementation Details

- **Language**: Python  
- **Libraries**:
  - OpenCV (camera processing)
  - MediaPipe (hand landmark detection)
  - e_drone (CoDrone Mini control SDK)
  - NumPy (mathematical operations)

- **Environment**:
  - Conda virtual environment
  - Bluetooth communication with CoDrone Mini

---

## 📂 Code Structure & Development Stages

The following table summarizes the development stages and the role of each script used in this project.

| 단계 | 주요 파일 | 역할 |
|------|----------|------|
| 카메라 테스트 | `camera_test.py` | 웹캠 동작 확인 |
| 손 인식 디버깅 | `hand_debug.py` | 손 랜드마크 시각화 (MediaPipe) |
| 제스처 안정화 | `gesture_stable_command.py` | 손가락 개수 → 숫자 계산 |
| 드론 제어 실험 | `drone_basic_test.py` | 이동 파라미터 실험 및 튜닝 |
| 드론 미션 설계 | `drone_missions.py` | 숫자별 드론 동작 매핑 |
| 통합 제어 | `main_gesture_to_drone.py` | 제스처 → 드론 제어 통합 시스템 구현|

---

## ⚠️ Limitations

- Flight time limited (~5 minutes)  
- Battery drain affects movement consistency    
- Motion precision limited by available sensors  

---

## 🎯 Design Philosophy

- ❌ Autonomous navigation  
- ❌ Complex control theory  
- ⭕ Real-time vision-to-hardware integration  
- ⭕ Stable execution logic  
- ⭕ Parameter tuning through real flight experiments  
- ⭕ Safety-first system design  

This project demonstrates how computer vision can be integrated with physical drone control,  
with a strong focus on real-world experimentation and reliability.
