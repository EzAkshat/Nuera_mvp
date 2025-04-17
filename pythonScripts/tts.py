import requests
import os
import time
import subprocess

def text_to_speech(text, api_key):
    url = "https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM"
    headers = {
        "xi-api-key": api_key,
        "Content-Type": "application/json"
    }
    data = {
        "text": text,
        "voice_settings": {"stability": 0.5, "similarity_boost": 0.5}
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        timestamp = int(time.time())
        audio_file = f"response_{timestamp}.mp3"
        with open(audio_file, "wb") as f:
            f.write(response.content)
        subprocess.Popen(['start', audio_file], shell=True)