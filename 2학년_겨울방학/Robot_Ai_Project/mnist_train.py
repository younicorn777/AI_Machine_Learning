import tensorflow as tf
from tensorflow.keras import layers, models

# 1. MNIST 데이터 로드
(x_train, y_train), (x_test, y_test) = tf.keras.datasets.mnist.load_data()

# 2. 정규화 + 차원 추가
x_train = x_train / 255.0
x_test  = x_test / 255.0
x_train = x_train[..., tf.newaxis]
x_test  = x_test[..., tf.newaxis]

# 3. 간단한 CNN 모델
model = models.Sequential([
    layers.Conv2D(16, (3,3), activation='relu', input_shape=(28,28,1)),
    layers.MaxPooling2D((2,2)),
    layers.Conv2D(32, (3,3), activation='relu'),
    layers.MaxPooling2D((2,2)),
    layers.Flatten(),
    layers.Dense(64, activation='relu'),
    layers.Dense(10, activation='softmax')
])

# 4. 컴파일
model.compile(
    optimizer='adam',
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

# 5. 학습
model.fit(x_train, y_train, epochs=3, validation_split=0.1)

# 6. 테스트
test_loss, test_acc = model.evaluate(x_test, y_test)
print("Test accuracy:", test_acc)

# 7. 모델 저장
model.save("mnist_cnn.h5")
print("Model saved as mnist_cnn.h5")