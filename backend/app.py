from flask import Flask, request, jsonify
from flask_cors import CORS
import librosa
import numpy as np
import tensorflow as tf
import os

app = Flask(__name__)

CORS(app, origins="*", supports_credentials=True) 

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


model = tf.keras.models.load_model('model/emotion_model.h5')

EMOTIONS = ['Anger', 'Disgust', 'Fear', 'Happy', 'Neutral', 'Sad']

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
    file.save(filepath)

    audio, sr = librosa.load(filepath, sr=None)
    features = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=40).mean(axis=1)
    features = np.expand_dims(features, axis=0)

    prediction = model.predict(features)
    emotion = EMOTIONS[np.argmax(prediction)]
    confidence = float(np.max(prediction))

    return jsonify({"emotion": emotion, "confidence": confidence})

if __name__ == '__main__':
    app.run(debug=True)
