import sounddevice as sd
import numpy as np
import pyautogui
import time

THRESHOLD_MULTIPLIER = 3.0      # How much louder than background noise a clap must be
DOUBLE_CLAP_TIME = 0.5          # Max time gap between claps for double clap
BACKGROUND_UPDATE_RATE = 0.1    # How often to update background noise (seconds)

last_clap_time = 0
clap_count = 0
background_noise = 0.05  # Starting guess

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

with sd.InputStream(callback=clap_detect):
    print("Listening for claps... Single clap = Pause/Play, Double clap = Mute/Unmute")
    while True:
        pass
    