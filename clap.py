# clap.py
from flask import Flask, render_template, request
import sounddevice as sd
import numpy as np
import pyautogui
import time
import threading

app = Flask(__name__)

# Clap detection settings
THRESHOLD_MULTIPLIER = 3.0
DOUBLE_CLAP_TIME = 0.5
BACKGROUND_UPDATE_RATE = 0.1

last_clap_time = 0
clap_count = 0
background_noise = 0.05  # Starting guess
listening = False  # Flag to control listening
stream = None      # Sound stream object

# Lock for thread-safe access to global variables
lock = threading.Lock()

def clap_detect(indata, frames, time_info, status):
    global last_clap_time, clap_count, background_noise

    volume_norm = np.linalg.norm(indata) * 10

    # Update background noise level gradually
    if time.time() - last_clap_time > BACKGROUND_UPDATE_RATE:
        background_noise = (background_noise * 0.9) + (volume_norm * 0.1)

    # Clap detection based on spike over background
    if volume_norm > background_noise * THRESHOLD_MULTIPLIER:
        current_time = time.time()

        if current_time - last_clap_time <= DOUBLE_CLAP_TIME:
            clap_count += 1
        else:
            clap_count = 1

        last_clap_time = current_time

        if clap_count == 1:
            pyautogui.press('space')
            print("👏 Single clap: Pause/Play toggled.")

        elif clap_count == 2:
            pyautogui.press('m')
            print("👏👏 Double clap: Mute/Unmute toggled.")
            clap_count = 0

def start_listening():
    global listening, stream
    with lock:
        if not listening:
            listening = True
            stream = sd.InputStream(callback=clap_detect)
            stream.start()
            print("Started listening for claps...")
            return "Listening"
        return "Already listening"

def stop_listening():
    global listening, stream
    with lock:
        if listening and stream:
            stream.stop()
            stream.close()
            listening = False
            print("Stopped listening for claps.")
            return "Stopped"
        return "Not listening"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/control', methods=['POST'])
def control():
    action = request.form.get('action')
    if action == "start":
        status = start_listening()
    elif action == "stop":
        status = stop_listening()
    else:
        status = "Invalid action"
    return status  # Return status to the frontend

if __name__ == '__main__':
    app.run(debug=True)
