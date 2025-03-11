from flask import Flask, render_template, request, redirect, url_for
import os
import shutil
import urllib.request
from vosk import Model, KaldiRecognizer
import wave
import json

app = Flask(__name__)
VOSK_MODEL_PATH = "/tmp/vosk-model-small-en-us-0.15"
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MODEL_FOLDER'] = '/tmp/vosk-model'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Function to download Vosk model if not present
def download_model():
    model_path = app.config['MODEL_FOLDER']
    if not os.path.exists(model_path):
        print("Downloading Vosk model...")
        url = 'https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip'
        zip_path = '/tmp/vosk-model.zip'
        urllib.request.urlretrieve(url, zip_path)
        shutil.unpack_archive(zip_path, '/tmp/')
        # Move unpacked folder to expected location
        unpacked_name = '/tmp/vosk-model-small-en-us-0.15'
        os.rename(unpacked_name, model_path)
        print("Model downloaded and extracted.")

# Call this when app starts
download_model()

# Load Vosk model
model = Model(app.config['MODEL_FOLDER'])

@app.route('/')
def index():
    return "Hello, world!"

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            return "No file part", 400
        file = request.files['file']
        if file.filename == '':
            return "No selected file", 400
        if file:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            timestamps = transcribe_audio(filepath)
            return render_template('results.html', filename=file.filename, timestamps=timestamps)
    return render_template('upload.html')

# Transcribe audio and get word-level timestamps
def transcribe_audio(filepath):
    wf = wave.open(filepath, "rb")
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
        return "Audio file must be WAV format mono PCM."

    rec = KaldiRecognizer(model, wf.getframerate())
    rec.SetWords(True)
    results = []
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            res = json.loads(rec.Result())
            if 'result' in res:
                results.extend(res['result'])
    final_res = json.loads(rec.FinalResult())
    if 'result' in final_res:
        results.extend(final_res['result'])

    return results  # List of words with start, end, word

# Route to serve uploaded audio files
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)
