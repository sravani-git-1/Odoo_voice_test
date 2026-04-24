import streamlit as st
import requests
from faster_whisper import WhisperModel
from gtts import gTTS
import tempfile
from datetime import datetime

# ==============================
# 🔧 CONFIG
# ==============================
N8N_WEBHOOK_URL = "https://yashwanthrt1.app.n8n.cloud/webhook/smart_voice_agent"

# ==============================
# 🎤 LOAD WHISPER MODEL
# ==============================
@st.cache_resource
def load_model():
    return WhisperModel("tiny", device="cpu", compute_type="int8")

model = load_model()

# ==============================
# 🧠 SPEECH → TEXT (ENGLISH ONLY)
# ==============================
def speech_to_text(audio_file):
    segments, _ = model.transcribe(audio_file, language="en")
    text = " ".join([seg.text for seg in segments])
    return text.strip()

# ==============================
# 🌐 SEND TO N8N
# ==============================
def send_to_n8n(message):
    try:
        res = requests.post(N8N_WEBHOOK_URL, json={"message": message})

        print("STATUS:", res.status_code)
        print("RAW RESPONSE:", res.text)

        if not res.text:
            return "No response from server"

        try:
            data = res.json()
            return data.get("response", "")
        except:
            return res.text

    except Exception as e:
        return f"Error: {str(e)}"

# ==============================
# 🔊 TEXT → SPEECH
# ==============================
def speak(text):
    if not text or str(text).strip() == "":
        return  # prevent crash

    try:
        tts = gTTS(text=text, lang="en")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
            tts.save(fp.name)
            audio_file = open(fp.name, "rb")
            st.audio(audio_file.read(), format="audio/mp3")

    except Exception as e:
        st.error(f"TTS Error: {e}")

# ==============================
# 📝 LOG CHAT
# ==============================
def save_chat(user, ai):
    with open("chat_log.txt", "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now()}]\n")
        f.write(f"User: {user}\n")
        f.write(f"AI: {ai}\n")
        f.write("-" * 40 + "\n")

# ==============================
# 🎨 UI
# ==============================
st.set_page_config(page_title="Voice ERP Assistant")

st.title("🎤 Smart Voice ERP Assistant")
st.caption("Speak → AI → Voice Response")

st.markdown("### 🎙 Speak now")

# 🎤 Audio input (native Streamlit)
audio = st.audio_input("Click and speak")

if audio:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
        f.write(audio.read())
        audio_path = f.name

    # 🧠 Speech to text
    user_text = speech_to_text(audio_path)

    if user_text:
        st.markdown("### 🧑 You said:")
        st.write(user_text)

        # 🌐 Send to n8n
        response = send_to_n8n(user_text)

        st.markdown("### 🤖 AI Response:")
        st.write(response)

        # 🔊 Speak
        speak(response)

        # 📝 Save log
        save_chat(user_text, response)

    else:
        st.warning("Could not understand audio. Try again.")