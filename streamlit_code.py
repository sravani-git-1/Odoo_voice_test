import streamlit as st
import requests
import json
from gtts import gTTS
import io
from faster_whisper import WhisperModel

# ---------------- CONFIG ----------------
N8N_WEBHOOK_URL = "YOUR_N8N_WEBHOOK_URL"

st.set_page_config(page_title="Smart Voice ERP Assistant")
st.title("🎤 Smart Voice ERP Assistant")

# ---------------- LOAD WHISPER ----------------
@st.cache_resource
def load_model():
    return WhisperModel("tiny", device="cpu", compute_type="int8")

model = load_model()

# ---------------- SPEECH → TEXT ----------------
def speech_to_text(file):
    try:
        with open("temp.wav", "wb") as f:
            f.write(file.read())

        segments, _ = model.transcribe("temp.wav")
        text = " ".join([seg.text for seg in segments])
        return text.strip()

    except Exception as e:
        return f"Error in STT: {str(e)}"

# ---------------- SEND TO N8N ----------------
def send_to_n8n(message):
    try:
        res = requests.post(N8N_WEBHOOK_URL, json={"message": message})

        try:
            result = res.json()
        except:
            return res.text

        if isinstance(result, dict) and "response" in result:
            return result["response"]

        if isinstance(result, dict):
            return json.dumps(result, indent=2)

        return str(result)

    except Exception as e:
        return f"Error: {str(e)}"

# ---------------- TEXT → SPEECH ----------------
def speak(text):
    try:
        tts = gTTS(text=text, lang="en")
        audio_bytes = io.BytesIO()
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)
        st.audio(audio_bytes, format="audio/mp3")
    except:
        pass

# ---------------- TEXT INPUT ----------------
st.subheader("💬 Text Input")
user_text = st.text_input("Type your message:")

if st.button("Send Text"):
    if user_text:
        st.chat_message("user").write(user_text)

        response = send_to_n8n(user_text)

        st.chat_message("assistant").write(response)
        speak(response)

# ---------------- AUDIO UPLOAD ----------------
st.subheader("🎤 Upload Voice (WAV file)")
audio_file = st.file_uploader("Upload your voice file", type=["wav"])

if audio_file:
    st.audio(audio_file)

    st.info("Transcribing...")

    text = speech_to_text(audio_file)

    if text:
        st.chat_message("user").write(text)

        response = send_to_n8n(text)

        st.chat_message("assistant").write(response)
        speak(response)