import streamlit as st
import requests
from faster_whisper import WhisperModel
from gtts import gTTS
import io
import os
import datetime

# --- CONFIG ---
N8N_WEBHOOK_URL = "https://yashwanthrt1.app.n8n.cloud/webhook/smart_voice_agent"

# --- HELPERS ---

def log_to_file(user_text, bot_response):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}]\nUser: {user_text}\nAI: {bot_response}\n" + ("-"*40) + "\n"
    with open("chat_log.txt", "a", encoding="utf-8") as f:
        f.write(log_entry)

@st.cache_resource
def load_model():
    return WhisperModel("base", device="cpu", compute_type="int8")

def format_odoo_data(data):
    """Format list of customers/vendors nicely"""
    formatted = []
    for item in data:
        block = (
            f"👤 {item.get('name','')}\n"
            f"📞 {item.get('phone','')}\n"
            f"📱 {item.get('mobile','')}\n"
            f"📧 {item.get('email','')}\n"
            f"📍 {item.get('location','')}\n"
        )
        formatted.append(block)
    return "\n\n".join(formatted)

# --- INIT ---
st.set_page_config(page_title="Voice ERP Assistant", page_icon="🎤")
model = load_model()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Settings")

    lang_option = st.selectbox(
        "Language",
        ["en", "hi"],
        format_func=lambda x: "English" if x == "en" else "Hindi"
    )

    st.divider()

    if os.path.exists("chat_log.txt"):
        with open("chat_log.txt", "r", encoding="utf-8") as f:
            st.download_button("💾 Download Logs", f, file_name="chat_log.txt")

    if st.button("🧹 Clear Chat"):
        st.session_state.chat_history = []

# --- UI ---
st.title("🎤 Smart Voice ERP Assistant")
st.caption("Streamlit + n8n + FastAPI + Odoo")

# Show chat history
for role, msg in st.session_state.chat_history:
    st.chat_message(role).write(msg)

# --- AUDIO INPUT ---
audio = st.audio_input("Speak now...")

if audio:
    # Save temp audio
    with open("temp.wav", "wb") as f:
        f.write(audio.getbuffer())

    with st.spinner("👂 Listening..."):

        # --- STT ---
        segments, _ = model.transcribe("temp.wav", language=lang_option)
        transcript = "".join([s.text for s in segments]).strip()

        if not transcript:
            st.warning("Couldn't hear properly.")
            st.stop()

        # Show user message
        st.chat_message("user").write(transcript)
        st.session_state.chat_history.append(("user", transcript))

        # --- SEND TO n8n ---
        payload = {
            "chatInput": transcript,
            "source": "voice",
            "language": lang_option,
            "timestamp": str(datetime.datetime.now())
        }

        try:
            res = requests.post(N8N_WEBHOOK_URL, json=payload, timeout=20)

            if res.status_code != 200:
                ai_reply = f"❌ n8n Error: {res.status_code}"
            else:
                data = res.json()

                # --- HANDLE RESPONSE ---
                output = data.get("output", data)

                if isinstance(output, list):
                    # Odoo data
                    ai_reply = format_odoo_data(output)

                elif isinstance(output, dict):
                    ai_reply = str(output)

                else:
                    ai_reply = str(output)

        except requests.exceptions.Timeout:
            ai_reply = "⏳ Request timeout"
        except requests.exceptions.ConnectionError:
            ai_reply = "🔌 Cannot connect to n8n"
        except Exception as e:
            ai_reply = f"⚠️ Error: {str(e)}"

        # --- DISPLAY ---
        st.chat_message("assistant").write(ai_reply)
        st.session_state.chat_history.append(("assistant", ai_reply))

        # --- LOG ---
        log_to_file(transcript, ai_reply)

        # --- TTS ---
        try:
            tts = gTTS(text=ai_reply, lang=lang_option)
            audio_stream = io.BytesIO()
            tts.write_to_fp(audio_stream)
            st.audio(audio_stream, format="audio/mp3", autoplay=True)
        except:
            st.warning("TTS failed")

    # Cleanup
    if os.path.exists("temp.wav"):
        os.remove("temp.wav")