import librosa
import librosa.display
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import butter, lfilter
import tensorflow as tf
from tensorflow.keras import layers

# Load audio file
y, sr = librosa.load('audio_file.wav')

# Spectrogram visualization
D = librosa.amplitude_to_db(librosa.stft(y), ref=np.max)
plt.figure(figsize=(10, 6))
librosa.display.specshow(D, sr=sr, x_axis='time', y_axis='log')
plt.colorbar(format='%+2.0f dB')
plt.title('Spectrogram')
plt.show()

# Noise reduction
def butter_lowpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def lowpass_filter(data, cutoff, fs, order=5):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = lfilter(b, a, data)
    return y

y_filtered = lowpass_filter(y, cutoff=3000, fs=sr)

# Pitch shifting
y_shifted = librosa.effects.pitch_shift(y, sr, n_steps=2)

# Audio classifier using a simple neural network
def build_model(input_shape):
    model = tf.keras.Sequential([
        layers.Conv1D(32, 3, activation='relu', input_shape=input_shape),
        layers.MaxPooling1D(2),
        layers.Conv1D(64, 3, activation='relu'),
        layers.MaxPooling1D(2),
        layers.Flatten(),
        layers.Dense(64, activation='relu'),
        layers.Dense(2, activation='softmax')
    ])
    return model

# Example data preparation (replace with actual data)
X_train = np.random.rand(100, 22050, 1)  # 100 samples, 22050 features (1 second of audio at 22050 Hz)
y_train = np.random.randint(0, 2, 100)   # 100 labels (0 or 1)

model = build_model((22050, 1))
model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
model.fit(X_train, y_train, epochs=10, batch_size=32)