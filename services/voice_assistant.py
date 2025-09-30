import os
import re
import time
import wave
import sounddevice as sd
import soundfile as sf
import webrtcvad
from rapidfuzz import fuzz
import subprocess
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# --- Konfiguracja ---
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SAMPLE_RATE = 16000
CHANNELS = 1
FRAME_MS = 30
VAD_AGGRESSIVENESS = 1
VAD_SPEECH_THRESHOLD = 0.1
WAKE_PHRASE = ""
FUZZY_THRESHOLD = 60

client = OpenAI(api_key=OPENAI_API_KEY)

# mapa fraza → program
ACTIONS = {
    "cock": {
        "windows": ["calc.exe"],
        "darwin": ["open", "-a", "Calculator"]
    },
    # dodaj kolejne tutaj
}


def record_chunk(duration, filename):
    print(f"[voice_assistant] Nagrywam {duration}s audio do {filename} …")
    data = sd.rec(int(duration * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=CHANNELS)
    sd.wait()
    sf.write(filename, data, SAMPLE_RATE)
    return filename


def transcribe(audio_file):
    print(f"[voice_assistant] Transkrypcja {audio_file} (tylko EN)…")
    with open(audio_file, "rb") as f:
        resp = client.audio.transcriptions.create(
            model=WHISPER_MODEL,
            file=f,
            language="en",
            response_format="verbose_json"
        )
    data = resp.model_dump()
    segments = data.get("segments", [])
    text = " ".join(seg["text"].strip() for seg in segments)
    print(f"[voice_assistant] Rozpoznano: {text}")
    return text


def normalize(text):
    # usuwa znaki spoza ASCII i przestankowe
    t = re.sub(r'[^\x00-\x7F]', '', text)
    return re.sub(r'[^\w\s]', '', t).strip().lower()


def is_speech(audio_file):
    # sprawdza czy to w ogóle mowa czy szum
    with wave.open(audio_file, "rb") as wf:
        assert wf.getnchannels() == 1 and wf.getframerate() == SAMPLE_RATE
        pcm = wf.readframes(wf.getnframes())
    vad = webrtcvad.Vad(VAD_AGGRESSIVENESS)
    frame_len = int(SAMPLE_RATE * 30 / 1000) * 2  # 30ms frame, 2 bytes/sample
    frames = [pcm[i:i + frame_len] for i in range(0, len(pcm), frame_len)]
    if not frames:
        return False
    speech = sum(1 for f in frames if vad.is_speech(f, SAMPLE_RATE))
    ratio = speech / len(frames)
    print(f"[voice_assistant] VAD speech ratio: {ratio:.2f}")
    return ratio >= VAD_SPEECH_THRESHOLD


def is_wake(text):
    norm = normalize(text)
    print(f"[voice_assistant] Normalized text: '{norm}'")
    score = fuzz.partial_ratio(norm, WAKE_PHRASE)
    print(f"[voice_assistant] Fuzzy score for wake-phrase: {score}")
    return score >= FUZZY_THRESHOLD


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
