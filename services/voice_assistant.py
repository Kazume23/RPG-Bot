import os
import re
import time
import sounddevice as sd
import soundfile as sf
import subprocess
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Konfiguracja
SAMPLE_RATE = 16000
CHANNELS = 1
WAKE_DURATION = 3  # sekundy nagrywania frazy wake-word
CMD_DURATION = 3  # sekundy nagrywania komendy
WHISPER_MODEL = "whisper-1"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Inicjalizacja klienta OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

# Mapa fraza → program do uruchomienia
ACTIONS = {
    "cock": {
        "windows": ["calc.exe"],
        "darwin": ["open", "-a", "Calculator"]
    },
    # dodaj swoje kolejne komendy tutaj
}


def record_chunk(duration, filename):
    print(f"[voice_assistant] Nagrywam {duration}s audio do {filename}…")
    data = sd.rec(int(duration * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=CHANNELS)
    sd.wait()
    sf.write(filename, data, SAMPLE_RATE)
    return filename


def transcribe(audio_file):
    print(f"[voice_assistant] Transkrypcja {audio_file} (tylko angielski)…")
    with open(audio_file, "rb") as f:
        resp = client.audio.transcriptions.create(
            model=WHISPER_MODEL,
            file=f,
            language="en"  # wymuszamy tylko angielski
        )
    text = resp.text.strip()
    print(f"[voice_assistant] Rozpoznano: {text}")
    return text


def normalize(text):
    # usuń znaki przestankowe i zostaw tylko ASCII
    cleaned = re.sub(r'[^\x00-\x7F]', '', text)
    cleaned = re.sub(r'[^\w\s]', '', cleaned)
    return cleaned.strip().lower()


def is_wake(text):
    norm = normalize(text)
    print(f"[voice_assistant] Normalized wake-word: '{norm}'")
    return norm.startswith("hey shadow")


def handle_command(cmd_text):
    cmd = cmd_text.lower()
    for pattern, progs in ACTIONS.items():
        if pattern in cmd:
            prog = progs.get(os.name) or progs.get("windows")
            subprocess.Popen(prog)
            print(f"[voice_assistant] Uruchamiam: {prog}")
            return True
    print("[voice_assistant] Nie rozpoznano komendy.")
    return False


def listen_once():
    wake_file = record_chunk(WAKE_DURATION, "wake.wav")
    wake_text = transcribe(wake_file)
    if is_wake(wake_text):
        print("[voice_assistant] Wake-word wykryty!")
        cmd_file = record_chunk(CMD_DURATION, "cmd.wav")
        cmd_text = transcribe(cmd_file)
        handle_command(cmd_text)
    else:
        print("[voice_assistant] Wake-word nie wykryto.")


if __name__ == "__main__":
    listen_once()
