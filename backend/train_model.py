import os
import numpy as np
import librosa
import tensorflow as tf
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

# Dataset path
DATASET_PATH = "../dataset/"  # Adjust this path based on your structure

# Emotions to classify (from folder names)
EMOTIONS = [folder for folder in os.listdir(DATASET_PATH) if os.path.isdir(os.path.join(DATASET_PATH, folder))]

# Function to extract features
def extract_features(file_path, n_mfcc=40):
    audio, sr = librosa.load(file_path, sr=None)
    mfccs = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=n_mfcc)
    return np.mean(mfccs.T, axis=0)

# Load dataset and labels
def load_data(dataset_path):
    features, labels = [], []
    for emotion in EMOTIONS:
        emotion_path = os.path.join(dataset_path, emotion)
        for file_name in os.listdir(emotion_path):
            if file_name.endswith('.wav'):  # Only process .wav files
                try:
                    file_path = os.path.join(emotion_path, file_name)
                    feature = extract_features(file_path)
                    features.append(feature)
                    labels.append(emotion)
                except Exception as e:
                    print(f"Error processing {file_name}: {e}")
    return np.array(features), np.array(labels)

# Load features and labels
X, y = load_data(DATASET_PATH)

# Encode labels
label_encoder = LabelEncoder()
y = label_encoder.fit_transform(y)

# Split into train and test sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Build a model
model = tf.keras.Sequential([
    tf.keras.layers.Dense(256, activation='relu', input_shape=(X_train.shape[1],)),
    tf.keras.layers.Dropout(0.3),
    tf.keras.layers.Dense(128, activation='relu'),
    tf.keras.layers.Dropout(0.3),
    tf.keras.layers.Dense(len(EMOTIONS), activation='softmax')
])

# Compile the model
model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])

# Train the model
history = model.fit(X_train, y_train, validation_data=(X_test, y_test), epochs=20, batch_size=32)

# Save the model
os.makedirs('model', exist_ok=True)
model.save('model/emotion_model.h5')

print("Model trained and saved at 'model/emotion_model.h5'")
