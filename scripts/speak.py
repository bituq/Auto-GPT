import os
from playsound import playsound
import requests
from config import Config
cfg = Config()
import gtts
import threading
from threading import Lock


# TODO: Nicer names for these ids
voices = ["Cu5mXKLL386G6JhHFa0Y", "kVPvrPissHvLEgTIaF0d"]

tts_headers = {
    "Content-Type": "application/json",
    "xi-api-key": cfg.elevenlabs_api_key
}

mutex_lock = Lock() # Ensure only one sound is played at a time

def eleven_labs_speech(text, voice_index=0):
    tts_url = "https://api.elevenlabs.io/v1/text-to-speech/{voice_id}".format(
        voice_id=voices[voice_index])
    formatted_message = {"text": text, "voice_settings": {"stability": 0.3, "similarity_boost": 1}}
    response = requests.post(
        tts_url, headers=tts_headers, json=formatted_message)

    if response.status_code == 200:
        with mutex_lock:
            with open("speech.mpeg", "wb") as f:
                f.write(response.content)
            playsound("speech.mpeg", True)
            os.remove("speech.mpeg")
        return True
    else:
        print("Request failed with status code:", response.status_code)
        print("Response content:", response.content)
        return False

def gtts_speech(text):
    tts = gtts.gTTS(text)
    with mutex_lock:
        tts.save("speech.mp3")
        playsound("speech.mp3", True)
        os.remove("speech.mp3")

def say_text(text, voice_index=0):
    def speak():
        if not cfg.elevenlabs_api_key:
            gtts_speech(text)
        else:
            success = eleven_labs_speech(text, voice_index)
            if not success:
                gtts_speech(text)

    thread = threading.Thread(target=speak)
    thread.start()
