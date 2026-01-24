import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os

# ================== LOAD API KEY ==================
load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")

client = None
if api_key:
    client = OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1"
    )

# ================== PAGE CONFIG ==================
st.set_page_config(
    page_title="🌸 ManoSakhi",
    layout="centered"
)

# ================== STYLES ==================
st.markdown("""
<style>
.stApp { background-color: #0f0f0f; color: white; }
.header-card {
    background: #1c1c1c;
    padding: 18px;
    border-radius: 16px;
    text-align: center;
}
.user-bubble {
    background: #2e7d32;
    padding: 12px;
    border-radius: 14px;
    margin: 6px 0;
    max-width: 85%;
    margin-left: auto;
}
.bot-bubble {
    background: #1f1f1f;
    padding: 12px;
    border-radius: 14px;
    margin: 6px 0;
    max-width: 85%;
}
</style>
""", unsafe_allow_html=True)

# ================== HEADER ==================
st.markdown("""
<div class="header-card">
<h2>🌸 ManoSakhi</h2>
<p><b>Mental Health Chatbot</b></p>
<p>A safe space to talk 🤍</p>
<small>Emotional support only. Not medical advice.</small>
</div>
""", unsafe_allow_html=True)

st.info("🛡️ Emotional support only. Not a replacement for professional help.")

# ================== SESSION STATE ==================
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "last_bot_reply" not in st.session_state:
    st.session_state.last_bot_reply = ""

if "emotion" not in st.session_state:
    st.session_state.emotion = "neutral"

# ================== EMOTION DETECTION ==================
def detect_emotion(text):
    text = text.lower()

    if any(w in text for w in ["sad", "down", "cry", "hurt"]):
        return "sad"
    if any(w in text for w in ["angry", "mad", "fight", "argue"]):
        return "angry"
    if any(w in text for w in ["lonely", "alone", "ignored"]):
        return "lonely"
    if any(w in text for w in ["stress", "pressure", "exam", "anxious"]):
        return "anxious"
    if any(w in text for w in ["happy", "good", "better"]):
        return "positive"

    return "neutral"

# ================== CRISIS CHECK ==================
def crisis_check(text):
    keywords = [
        "suicide", "kill myself", "end my life",
        "self harm", "cut myself", "die"
    ]
    return any(k in text.lower() for k in keywords)

# ================== GROUNDING ==================
def grounding_exercise():
    return (
        "Let’s slow down together for a moment 🤍\n\n"
        "🫁 Breathe in for 4 seconds…\n"
        "Hold for 2 seconds…\n"
        "Breathe out slowly for 6 seconds.\n\n"
        "Look around and notice:\n"
        "• 5 things you see\n"
        "• 4 things you feel\n"
        "• 3 things you hear\n\n"
        "I’m right here with you."
    )

# ================== LOCAL SUPPORT ==================
def local_support_response(text, emotion):
    if emotion == "sad":
        return (
            "I’m really sorry you’re feeling this way. Sadness can feel heavy.\n\n"
            "What’s the part that hurts the most right now?"
        )
    if emotion == "angry":
        return (
            "It sounds like there’s a lot of emotion after what happened.\n\n"
            "Do you feel more angry, or more hurt by the situation?"
        )
    if emotion == "lonely":
        return (
            "Feeling lonely can be very painful.\n\n"
            "When did you start feeling this way?"
        )
    if emotion == "anxious":
        return (
            "That sounds stressful.\n\n"
            "Is your mind racing, or does your body feel tense right now?"
        )

    return "I’m listening. Tell me more when you’re ready."

# ================== CHAT FUNCTION ==================
def chat_with_ai(user_input):

    # Crisis handling
    if crisis_check(user_input):
        return (
            "I’m really glad you shared this with me.\n\n"
            "You don’t have to face this alone.\n\n"
            "📞 India Suicide Helpline: 9152987821\n"
            "🌍 Global Help: https://findahelpline.com\n\n"
            f"{grounding_exercise()}"
        )

    # Emotion detection
    emotion = detect_emotion(user_input)
    st.session_state.emotion = emotion

    # AI RESPONSE
    if client:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are ManoSakhi, an empathetic emotional support chatbot. "
                    "Acknowledge emotions clearly. Avoid repeating questions. "
                    "Give gentle, specific responses. No medical advice."
                )
            }
        ]

        for role, msg in st.session_state.chat_history[-6:]:
            messages.append({
                "role": "assistant" if role == "bot" else "user",
                "content": msg
            })

        messages.append({"role": "user", "content": user_input})

        try:
            response = client.chat.completions.create(
                model="mistralai/mistral-7b-instruct:free",
                messages=messages,
                timeout=20
            )

            reply = response.choices[0].message.content.strip()

            if reply == st.session_state.last_bot_reply:
                reply += "\n\nI’m here with you."

            return reply

        except Exception:
            pass

    return local_support_response(user_input, emotion)

# ================== CHAT DISPLAY ==================
for role, msg in st.session_state.chat_history:
    if role == "user":
        st.markdown(f"<div class='user-bubble'>🧑 You<br>{msg}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='bot-bubble'>🤖 ManoSakhi<br>{msg}</div>", unsafe_allow_html=True)

# ================== INPUT ==================
user_input = st.text_input("✍️ Type your thoughts here (English only)")
send = st.button("Send ✉️")

if send and user_input.strip():
    reply = chat_with_ai(user_input)

    st.session_state.chat_history.append(("user", user_input))
    st.session_state.chat_history.append(("bot", reply))
    st.session_state.last_bot_reply = reply

    st.rerun()
