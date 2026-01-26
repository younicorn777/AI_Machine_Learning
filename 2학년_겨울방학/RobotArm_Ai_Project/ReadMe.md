# 🤖 CNN-Based Digit Recognition with Robotic Arm

---

## 🇰🇷 프로젝트 요약 (Korean Summary)

본 프로젝트는 카메라로 입력된 손글씨 숫자를 CNN으로 인식하고,  
그 결과를 로봇팔의 물리적 동작(포인팅)으로 연결하는 시스템입니다.  
MNIST 데이터셋으로 학습된 CNN 모델을 실제 환경에 적용하기 위해,  
입력 이미지 전처리와 인식 안정성 판단에 중점을 두었습니다.  
모델 구조 변경보다는 시스템 설계와 신뢰성 확보를 목표로 진행한 프로젝트입니다.

---

## 📌 Project Overview

This project implements a real-time digit recognition system using a CNN model
and applies the recognition result to control a robotic arm as a physical output device.

A handwritten digit shown to a camera is recognized by a CNN trained on the MNIST dataset,
and the robotic arm points to the corresponding number on a board.

Rather than focusing on CNN architecture tuning, this project emphasizes
**system-level design**, especially preprocessing and stability of inference results
in real-world environments.

---

## 🧠 Image Preprocessing Pipeline

The CNN model was trained on MNIST images (28×28, grayscale, centered digits).
Therefore, the camera input image must be transformed to closely match this format.

### 🔄 Overall Pipeline

### 1. Grayscale Conversion
- Removes color information
- Emphasizes digit shape and structure

### 2. Gaussian Blur
- Reduces camera noise
- Stabilizes binary thresholding

### 3. Binary Thresholding
- Separates digit from background
- Uses Otsu’s method for adaptive thresholding

### 4. Morphological Processing
- Connects broken strokes
- Reinforces thin digit lines

### 5. ROI Extraction with Margin
- Extracts only the digit region
- Prevents cropping of digit edges

### 6. Center Alignment
- Aligns digit to the image center
- Matches MNIST-style digit distribution

### 7. Resize & Normalization
- Resizes image to 28×28
- Normalizes pixel values to [0, 1]

---

## 🔧 Implementation Details

- **Language**: Python
- **Libraries**:
  - OpenCV (image processing)
  - TensorFlow (CNN inference)
  - NumPy (array operations)
  - PySerial (Arduino communication)

To avoid unstable robot behavior, the system confirms a digit only when:
- The same digit is predicted continuously for 3.5 seconds
- The confidence margin between the top-1 and top-2 predictions is sufficient

---

## 🎯 Design Philosophy

- ❌ Model architecture optimization
- ⭕ Input data quality improvement
- ⭕ Robust preprocessing
- ⭕ Stable system behavior in real-world conditions

This approach significantly reduced misclassification issues such as
7→4 and 9→4 observed during early testing.

---

## 📂 Code Structure & Development Stages

The following table summarizes the development stages and the role of each script used in this project.

| 단계 | 주요 파일 | 역할 |
|------|----------|------|
| 카메라 입력 | `camera_test.py`<br>`camera_gray.py`<br>`camera_binary.py` | 카메라 입력 및 영상 전처리 실험 |
| 숫자 추출 | `digit_roi.py` | 숫자 영역(ROI) 추출 및 검증 |
| CNN 준비 | `mnist_train.py`<br>`mnist_cnn.h5` | 숫자 인식용 CNN 모델 학습 및 저장 |
| 통신 테스트 | `serial_test.py` | Python–Arduino 시리얼 통신 검증 |
| 통합 / 시연 | `digit_predict_live_stable.py` | 전처리·CNN·안정성 판단·로봇 제어를 통합한 최종 결과 |

## 📝 Note

This project focuses on integrating AI inference with a physical robotic system
and ensuring reliable operation in non-ideal, real-world environments.
