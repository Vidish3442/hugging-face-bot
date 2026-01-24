import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os

# ================= LOAD API KEY =================
load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")

client = None
if api_key:
    client = OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1"
    )

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="🌸 ManoSakhi",
    layout="centered"
)

# ================= UI STYLE =================
st.markdown("""
<style>
.stApp { background-color: #0f0f0f; color: white; }
.header-card {
    background: #1c1c1c;
    padding: 18px;
    border-radius: 16px;
    text-align: center;
    margin-bottom: 10px;
}
.user-bubble {
    background: #2e7d32;
    padding: 12px 16px;
    border-radius: 14px;
    margin: 6px 0;
    max-width: 85%;
    margin-left: auto;
}
.bot-bubble {
    background: #1f1f1f;
    padding: 12px 16px;
    border-radius: 14px;
    margin: 6px 0;
    max-width: 85%;
}
</style>
""", unsafe_allow_html=True)

# ================= HEADER =================
st.markdown("""
<div class="header-card">
<h2>🌸 ManoSakhi</h2>
<p><b>Mental Health Chatbot</b></p>
<p>A safe space to talk 🤍</p>
<small>Emotional support only. Not medical advice.</small>
</div>
""", unsafe_allow_html=True)

st.info("🛡️ Emotional support only. Not a replacement for professional help.")

# ================= SESSION STATE =================
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "last_bot_reply" not in st.session_state:
    st.session_state.last_bot_reply = ""

# ================= MODEL PRIORITY =================
MODELS = [
    "openchat/openchat-7b:free",
    "mistralai/mistral-7b-instruct:free"
]

# ================= SYSTEM PROMPT =================
SYSTEM_PROMPT = """
You are ManoSakhi, a compassionate mental health support chatbot.

Rules:
- Respond with empathy, warmth, and seriousness.
- If the user mentions physical violence, being beaten, or harm by others, acknowledge it clearly.
- Do NOT minimize or ignore violence.
- Avoid repeating the same question.
- Ask gentle, open-ended follow-up questions.
- Offer emotional support and grounding suggestions when appropriate.
- Do NOT give medical or legal advice.
- Use simple, calm, human language.
"""

# ================= CRISIS CHECK =================
def crisis_check(text):
    keywords = [
        "suicide", "kill myself", "end my life",
        "self harm", "cut myself", "die"
    ]
    return any(k in text.lower() for k in keywords)

# ================= GROUNDING =================
def grounding_exercise():
    return (
        "Let’s pause together for a moment 🤍\n\n"
        "🫁 Breathe in slowly for 4 seconds…\n"
        "Hold for 2 seconds…\n"
        "Breathe out gently for 6 seconds.\n\n"
        "You’re not alone right now."
    )

# ================= CHAT FUNCTION =================
def chat_with_ai(user_input):

    # Self-harm crisis handling ONLY
    if crisis_check(user_input):
        return (
            "I’m really glad you told me this.\n\n"
            "You don’t have to face this alone.\n\n"
            "📞 India Suicide Helpline: 9152987821\n"
            "🌍 Global Help: https://findahelpline.com\n\n"
            f"{grounding_exercise()}"
        )

    # Build conversation context
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    for role, msg in st.session_state.chat_history[-8:]:
        messages.append({
            "role": "assistant" if role == "bot" else "user",
            "content": msg
        })

    messages.append({"role": "user", "content": user_input})

    # Try models in order
    if client:
        for model in MODELS:
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=messages,
                    timeout=20
                )

                reply = response.choices[0].message.content.strip()

                # Prevent repetition
                if reply == st.session_state.last_bot_reply:
                    reply += "\n\nI’m here with you. Take your time."

                return reply

            except Exception:
                continue

    # Emergency fallback (rare)
    return (
        "I’m really sorry you’re going through this.\n\n"
        "What you shared sounds painful, and I’m here to listen."
    )

# ================= CHAT DISPLAY =================
for role, msg in st.session_state.chat_history:
    if role == "user":
        st.markdown(
            f"<div class='user-bubble'>🧑 <b>You</b><br>{msg}</div>",
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"<div class='bot-bubble'>🤖 <b>ManoSakhi</b><br>{msg}</div>",
            unsafe_allow_html=True
        )

# ================= INPUT =================
st.markdown("---")
user_input = st.text_input("✍️ Type your thoughts here (English only)")
send = st.button("Send ✉️")

if send and user_input.strip():
    reply = chat_with_ai(user_input)

    st.session_state.chat_history.append(("user", user_input))
    st.session_state.chat_history.append(("bot", reply))
    st.session_state.last_bot_reply = reply

    st.rerun()
