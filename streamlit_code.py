import streamlit as st
import requests
import io
from gtts import gTTS
from faster_whisper import WhisperModel
from datetime import datetime

# ---------------- CONFIG ----------------
N8N_WEBHOOK_URL = "https://yashwanthrt1.app.n8n.cloud/webhook/smart_voice_agent"
LOG_FILE = "chat_log.txt"

st.set_page_config(page_title="Voice ERP Assistant")
st.title("🎤 Smart Voice ERP Assistant")

# ---------------- LOAD MODEL ----------------
@st.cache_resource
def load_model():
    return WhisperModel("tiny", device="cpu", compute_type="int8")

model = load_model()

# ---------------- SPEECH TO TEXT ----------------
def speech_to_text(audio_file):
    with open("temp.wav", "wb") as f:
        f.write(audio_file.getvalue())

    segments, _ = model.transcribe("temp.wav", language="en")
    text = " ".join([seg.text for seg in segments])
    return text.strip()

# ---------------- SEND TO N8N (SAFE VERSION) ----------------
def send_to_n8n(message):
    try:
        res = requests.post(N8N_WEBHOOK_URL, json={"message": message})

        # ✅ handle empty / invalid response
        if not res.text:
            return "No response from server"

        try:
            data = res.json()
            return data.get("response", str(data))
        except:
            return res.text  # fallback if not JSON

    except Exception as e:
        return f"Error: {str(e)}"

# ---------------- TEXT TO SPEECH ----------------
def speak(text):
    tts = gTTS(text=text, lang="en")
    audio_bytes = io.BytesIO()
    tts.write_to_fp(audio_bytes)
    audio_bytes.seek(0)
    st.audio(audio_bytes, format="audio/mp3")

# ---------------- SAVE LOG ----------------
def save_chat(user_text, ai_response):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{timestamp}\n")
        f.write(f"User: {user_text}\n")
        f.write(f"AI: {ai_response}\n")
        f.write("-" * 30 + "\n")

# ---------------- UI ----------------
st.subheader("🎙️ Speak now")

audio = st.audio_input("Click mic and speak")

# ---------------- PROCESS ----------------
if audio is not None:
    st.audio(audio)

    # 🎤 Speech → Text
    user_text = speech_to_text(audio)

    st.markdown("### 🧑 You said:")
    st.write(user_text)

    # 🤖 AI Response
    response = send_to_n8n(user_text)

    st.markdown("### 🤖 AI Response:")
    st.write(response)

    # 🔊 Speak
    speak(response)

    # 💾 Save log
    save_chat(user_text, response)