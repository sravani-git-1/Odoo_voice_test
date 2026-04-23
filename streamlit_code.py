import streamlit as st
import requests
import json
from gtts import gTTS
import io

# ---------------- CONFIG ----------------
N8N_WEBHOOK_URL = "YOUR_N8N_WEBHOOK_URL"  # 🔥 replace this

st.set_page_config(page_title="Smart Voice ERP Assistant")

st.title("🎤 Smart Voice ERP Assistant")
st.write("Streamlit + n8n + FastAPI + Odoo")

# ---------------- FUNCTION: SEND TO N8N ----------------
def send_to_n8n(message):
    try:
        payload = {
            "message": message
        }

        res = requests.post(N8N_WEBHOOK_URL, json=payload)

        # ✅ Parse JSON safely
        try:
            result = res.json()
        except:
            return res.text

        # ✅ If response key exists → return clean text
        if isinstance(result, dict) and "response" in result:
            return result["response"]

        # ✅ If CRUD JSON → return formatted JSON
        if isinstance(result, dict):
            return json.dumps(result, indent=2)

        return str(result)

    except Exception as e:
        return f"Error: {str(e)}"


# ---------------- FUNCTION: TEXT TO SPEECH ----------------
def speak(text):
    try:
        tts = gTTS(text=text, lang='en')
        audio_bytes = io.BytesIO()
        tts.write_to_fp(audio_bytes)
        audio_bytes.seek(0)
        st.audio(audio_bytes, format="audio/mp3")
    except:
        pass


# ---------------- INPUT ----------------
user_input = st.text_input("Speak or type your message:")

if st.button("Send") and user_input:
    st.chat_message("user").write(user_input)

    response = send_to_n8n(user_input)

    # ---------------- DISPLAY RESPONSE ----------------
    st.chat_message("assistant").write(response)

    # ---------------- VOICE OUTPUT ----------------
    speak(response)