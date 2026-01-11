import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os

# ------------------ Load API Key ------------------
load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")

# OpenRouter client (OpenAI-compatible)
client = None
if api_key:
    client = OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1"
    )

# ------------------ UI ------------------
st.set_page_config(page_title="🌸 ManoSakhi 🌸")
st.title("🌸 ManoSakhi – Mental Health Chatbot 🌸")
st.markdown("A safe space to talk 🤍")
st.caption("⚠️ Emotional support only. Not medical advice.")

# ------------------ Session ------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ------------------ Crisis Check ------------------
def crisis_check(text):
    words = [
        "suicide", "kill myself", "end my life",
        "self harm", "cut myself", "die"
    ]
    return any(w in text.lower() for w in words)

# ------------------ Local Fallback ------------------
def local_support_response(text):
    text = text.lower()

    if "sad" in text or "down" in text:
        return (
            "I'm really sorry you're feeling sad. That can feel heavy.\n\n"
            "Would you like to share what’s been making you feel this way?"
        )

    if "lonely" in text or "alone" in text:
        return (
            "Feeling lonely can be very painful.\n\n"
            "You’re not alone here. What’s been making you feel this way?"
        )

    if "stress" in text or "overwhelmed" in text:
        return (
            "It sounds like things have been overwhelming for you.\n\n"
            "What’s been causing the most stress lately?"
        )

    return (
        "I'm here with you and I'm listening.\n\n"
        "Tell me more about what’s been on your mind."
    )

# ------------------ Chat Function ------------------
def chat_with_ai(user_input):

    # Crisis handling (no API)
    if crisis_check(user_input):
        return (
            "I'm really glad you reached out. You matter.\n\n"
            "If you’re feeling unsafe, please talk to someone right now.\n\n"
            "📞 India: 9152987821\n"
            "🌍 Global: https://findahelpline.com"
        )

    # Try OpenRouter first
    if client:
        models = [
            "mistralai/mistral-7b-instruct:free",
            "openchat/openchat-7b:free"
        ]

        for model in models:
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "system",
                            "content": (
                                "You are a kind, empathetic mental health support chatbot. "
                                "Respond in simple, supportive English. "
                                "Do not give medical advice."
                            )
                        },
                        {"role": "user", "content": user_input}
                    ],
                    timeout=20
                )

                reply = response.choices[0].message.content
                if reply and reply.strip():
                    return reply.strip()

            except Exception:
                continue  # try next model

    # Always-safe local response
    return local_support_response(user_input)

# ------------------ Input ------------------
user_input = st.text_input(
    "✍️ Type your thoughts here (English only)",
    placeholder="Example: I feel sad today..."
)

if st.button("Send ✉️") and user_input.strip():
    reply = chat_with_ai(user_input)
    st.session_state.chat_history.append(("user", user_input))
    st.session_state.chat_history.append(("bot", reply))

# ------------------ Display ------------------
st.markdown("---")
for role, msg in st.session_state.chat_history:
    if role == "user":
        st.markdown(f"🧑 **You:** {msg}")
    else:
        st.markdown(f"🤖 **ManoSakhi:** {msg}")
