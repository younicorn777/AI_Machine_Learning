'''
mnist_train의 Docstring

MNIST 손글씨 숫자 인식을 위한 간단한 CNN 학습 코드

이 코드의 목적:
- MNIST 데이터셋(28x28 흑백 손글씨 숫자)을 불러와서 CNN 모델을 학습
- CNN 구조: Conv2D → MaxPooling → Conv2D → MaxPooling → Flatten → Dense → Dense
- 학습 후 테스트 정확도를 출력하고, 학습된 모델을 파일로 저장한다.

'''

import tensorflow as tf
from tensorflow.keras import layers, models

# 1. MNIST 데이터 로드
# MNIST: 28x28 픽셀의 손글씨 숫자 (0~9)
(x_train, y_train), (x_test, y_test) = tf.keras.datasets.mnist.load_data()

# 2. 정규화 + 차원 추가
# 픽셀 값 범위: 0~255 -> 0~1로 정규화 (학습 안정화)
x_train = x_train / 255.0
x_test  = x_test / 255.0

# CNN 입력은 (height, width, channel) 형태 필요
# MNIST는 흑백이라 channel=1을 추가 (RGB 였다면, 3 채널)
x_train = x_train[..., tf.newaxis]
x_test  = x_test[..., tf.newaxis]

# 3. 간단한 CNN 모델
'''
Conv2D (특징 추출): 이미지 위를 작은 필터가 훑으며 선, 곡선 같은 특징을 찾아냄

MaxPooling2D (정보 압축): 중요한 특징만 남기고 이미지 크기를 줄임
-> 연산량을 줄이고 사소한 위치 변화에 강해짐

Flatten (데이터 펼치기): 2차원 특징 지도(Feature Map)를 1차원 긴 줄로 쭉 핌 
-> 이제 '그림'이 아니라 '수치 데이터'가 되어 판단(Dense) 단계로 넘어감

Dense (판단): 펼쳐진 데이터를 보고 최종 결론을 내립니다.

마지막 Dense(10, activation='softmax')는 0부터 9까지 각 숫자일 확률 10개를 출력하며, 합은 항상 1(100%)이 됨.
'''
model = models.Sequential([
    layers.Conv2D(16, (3,3), activation='relu', input_shape=(28,28,1)),
    layers.MaxPooling2D((2,2)),
    layers.Conv2D(32, (3,3), activation='relu'),
    layers.MaxPooling2D((2,2)),
    layers.Flatten(),
    layers.Dense(64, activation='relu'),
    layers.Dense(10, activation='softmax')
])

# 4. 컴파일(학습 방법 설정)
# optimizer: Adam (가중치 업데이트 방법. 즉 학습방법)
# loss: sparse_categorical_crossentropy (예측과 정답의 차이를 수치화)(채점표)
# metrics: accuracy (학습 중에 성능을 확인하는 지표)

model.compile(
    optimizer='adam',
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

# 5. 학습
# epochs=3 -> 전체 데이터셋을 3번 반복 학습
# validation_split=0.1 -> 학습 데이터의 10%를 검증용으로 사용
model.fit(x_train, y_train, epochs=3, validation_split=0.1)

# 6. 테스트
# 학습하지 않은 테스트 데이터로 모델 성능 평가
test_loss, test_acc = model.evaluate(x_test, y_test)
print("Test accuracy:", test_acc)

# 7. 모델 저장
# 학습된 모델을 파일로 저장 (HDF5 형식)
model.save("mnist_cnn.h5")
print("Model saved as mnist_cnn.h5")