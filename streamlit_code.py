import streamlit as st
import requests
from faster_whisper import WhisperModel
from gtts import gTTS
import tempfile
from datetime import datetime

# ==============================
# CONFIG
# ==============================
N8N_WEBHOOK_URL = "https://yashwanthrt1.app.n8n.cloud/webhook/smart_voice_agent"

# ==============================
# LOAD MODEL
# ==============================
@st.cache_resource
def load_model():
    return WhisperModel("tiny", device="cpu", compute_type="int8")

model = load_model()

# ==============================
# SPEECH → TEXT
# ==============================
def speech_to_text(audio_file):
    segments, _ = model.transcribe(audio_file, language="en")
    return " ".join([seg.text for seg in segments]).strip()

# ==============================
# SEND TO N8N (FIXED)
# ==============================
def send_to_n8n(message):
    try:
        res = requests.post(N8N_WEBHOOK_URL, json={"message": message})

        # DEBUG (important)
        print("STATUS:", res.status_code)
        print("RAW:", res.text)

        if not res.text:
            return "❌ Empty response from server"

        try:
            data = res.json()

            # 🔥 HANDLE ALL CASES
            if "response" in data:
                return data["response"]
            elif "output" in data:
                return data["output"]
            elif "text" in data:
                return data["text"]
            else:
                return str(data)

        except:
            return res.text

    except Exception as e:
        return f"❌ Error: {str(e)}"

# ==============================
# TEXT → SPEECH
# ==============================
def speak(text):
    if not text.strip():
        return

    tts = gTTS(text=text, lang="en")

    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as fp:
        tts.save(fp.name)
        audio_file = open(fp.name, "rb")
        st.audio(audio_file.read(), format="audio/mp3")

# ==============================
# LOG
# ==============================
def save_chat(user, ai):
    with open("chat_log.txt", "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now()}]\nUser: {user}\nAI: {ai}\n{'-'*40}\n")

# ==============================
# PAGE UI
# ==============================
st.set_page_config(layout="wide")

st.markdown("""
<h1 style='text-align:center;'>🎤 Smart ERP Assistant</h1>
<p style='text-align:center;color:gray;'>Voice + Text AI Assistant</p>
""", unsafe_allow_html=True)

# ==============================
# SESSION STATE
# ==============================
if "text_user" not in st.session_state:
    st.session_state.text_user = ""
if "text_response" not in st.session_state:
    st.session_state.text_response = ""

# ==============================
# LAYOUT
# ==============================
col1, col2 = st.columns(2)

# ==============================
# VOICE
# ==============================
with col1:
    st.markdown("## 🎙 Voice Assistant")

    audio = st.audio_input("Click and speak")

    if audio:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
            f.write(audio.read())
            audio_path = f.name

        user_text = speech_to_text(audio_path)

        if user_text:
            st.write("### 🧑 You said:")
            st.write(user_text)

            response = send_to_n8n(user_text)

            st.write("### 🤖 AI Response:")
            st.write(response)

            speak(response)
            save_chat(user_text, response)

# ==============================
# TEXT (FULLY FIXED)
# ==============================
with col2:
    st.markdown("## 💬 Text Assistant")

    user_input = st.text_input("Enter your message", key="input_text")

    auto_speak = st.checkbox("🔊 Speak response")

    # ✅ IMPORTANT FIX → use form (prevents rerun issue)
    if st.button("Send"):
        if user_input.strip():
            response = send_to_n8n(user_input)

            st.session_state.text_user = user_input
            st.session_state.text_response = response

            save_chat(user_input, response)
        else:
            st.warning("Enter a message")

    # ✅ ALWAYS DISPLAY
    if st.session_state.text_user:
        st.write("### 🧑 You said:")
        st.write(st.session_state.text_user)

    if st.session_state.text_response:
        st.write("### 🤖 AI Response:")
        st.write(st.session_state.text_response)

        if auto_speak:
            speak(st.session_state.text_response)