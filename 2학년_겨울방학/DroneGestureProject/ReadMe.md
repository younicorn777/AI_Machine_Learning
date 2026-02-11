🚁 Gesture-Based Drone Control System
🇰🇷 프로젝트 요약 (Korean Summary)
본 프로젝트는 웹캠 영상에서 손 제스처를 인식하고,
손가락 개수를 숫자로 변환하여 드론의 물리적 동작(이륙, 이동, 착륙)으로 연결하는 시스템입니다.

MediaPipe 기반 손 랜드마크 추출과 e_drone 라이브러리를 활용하여
비전 인식 → 안정성 판단 → 하드웨어 제어 전체 흐름을 구현하였습니다.

단순 제스처 인식 구현을 넘어서,
실제 드론 비행 실험을 통해 발생한 문제를 해결하는 과정에 중점을 둔 프로젝트입니다.

📌 Project Overview
This project implements a real-time gesture recognition system that controls a drone using hand gestures detected from a webcam.

System Pipeline

Camera → Hand Landmark Detection → Finger Counting 
→ Stability Check → Drone Mission Execution
Rather than focusing only on gesture recognition accuracy,
this project emphasizes system stability, motion control reliability, and hardware-aware design decisions.

🧠 System Architecture
🔄 Overall Processing Flow
Camera Input (OpenCV)
Hand Landmark Detection (MediaPipe)
Finger Counting Logic
Stable Gesture Confirmation (1 second hold)
Drone Mission Mapping
Motion Execution with Brake & Hover Control
✋ Gesture Recognition Logic
The system detects hand landmarks using MediaPipe and counts extended fingers (0–5).

Finger Counting Strategy
Index / Middle / Ring / Pinky

Compare fingertip y-coordinate with lower joint
Thumb

Distance-based comparison between thumb tip and pinky base
More robust against palm/back orientation differences
⏱ Stability Logic
To avoid unintended drone motion:

The same gesture must be maintained for 1 second
After execution, the hand must be lowered before the next command
Edge-trigger structure prevents repeated execution
This prevents continuous command looping and accidental re-triggering.

🚁 Drone Motion Control Design
Real-world flight testing revealed several control challenges.

Instead of simple directional commands, the system uses structured control logic:

control() → raw motion control
brake() → short reverse thrust to remove inertia
hover() → trim-based stabilization
Movement Pattern
Move → Brake → Hover
This structure significantly improved motion stability.

🔧 Experimental Findings & Improvements
1️⃣ Hover Instability
Problem: Drone drifted during hover
Solution: Applied trim only in hover stage
2️⃣ Inertia After Movement
Problem: Drone did not stop immediately
Solution: Introduced brake control before hover
3️⃣ Unexpected Restart Behavior
Problem: After collision or disconnection, previous motion resumed
Solution: Implemented safe_initialize() routine
Repeated landing commands
Control value reset
4️⃣ Inconsistent Movement Results
Identical control values produced different distances
Cause: Real-time battery drain affects motor output
Limitation: No API access to real-time battery compensation
🧩 Final Gesture Mapping
Gesture	Action
1

Takeoff

2

Forward

3

Backward

4

Left

5

Right

0

Landing

🔧 Implementation Details
Language

Python
Libraries

OpenCV (camera processing)
MediaPipe (hand landmark detection)
e_drone (drone control SDK)
NumPy (mathematical utilities)
Environment

Conda virtual environment
Bluetooth communication with CoDrone Mini
📂 Code Structure
Stage	File	Role
Camera Test

camera_test.py

Webcam input verification

Hand Debug

hand_debug.py

Landmark visualization

Gesture Stability

gesture_stable_command.py

Stable gesture detection

Drone Basic Test

drone_basic_test.py

Motion parameter tuning

Drone Missions

drone_missions.py

Movement logic abstraction

Integration

main_gesture_to_drone.py

Full system integration

⚠️ Limitations
Battery drain affects motion consistency
No closed-loop position control implemented
Sensor-based compensation not integrated
Flight time limited (~5 minutes)
🎯 Design Philosophy
❌ Complex autonomous navigation
⭕ Stable real-time control
⭕ Hardware-aware parameter tuning
⭕ System-level reliability
⭕ Safety-first execution logic
This project demonstrates the integration of real-time computer vision with physical drone control, emphasizing stability and practical experimentation over theoretical optimization.

