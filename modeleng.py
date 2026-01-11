import streamlit as st
from huggingface_hub import InferenceClient
import os

# ------------------ API KEY ------------------
api_key = os.getenv("HUGGINGFACE_API_KEY")

if not api_key:
    st.error("HUGGINGFACE_API_KEY missing in Streamlit secrets")
    st.stop()

# ------------------ HF Client ------------------
client = InferenceClient(
    model="google/flan-t5-large",
    token=api_key
)

# ------------------ UI ------------------
st.set_page_config(page_title="🌸 ManoSakhi 🌸")
st.title("🌸 ManoSakhi – Mental Health Chatbot 🌸")
st.markdown("A safe space to talk 🤍")
st.caption("⚠️ This chatbot provides emotional support only.")

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

# ------------------ Chat Function ------------------
def chat_with_ai(user_input):

    # Crisis message (no API)
    if crisis_check(user_input):
        return (
            "I'm really glad you reached out. You matter.\n\n"
            "If you’re feeling unsafe, please reach out to a trusted person or a helpline immediately.\n\n"
            "📞 India: 9152987821\n"
            "🌍 Global: https://findahelpline.com"
        )

    prompt = (
        "You are a kind, empathetic mental health support chatbot.\n"
        "Respond in simple, supportive English.\n"
        "Do not give medical advice.\n\n"
        f"User says: {user_input}\n"
        "Your response:"
    )

    try:
        response = client.text_generation(
            prompt,
            max_new_tokens=120,
            temperature=0.6,
            top_p=0.9
        )

        if response and response.strip():
            return response.strip()

        # Empty response fallback
        return (
            "I'm really sorry you're feeling this way. "
            "Would you like to talk about what has been weighing on you?"
        )

    except Exception:
        # API failure fallback (VERY IMPORTANT)
        return (
            "I'm here with you. Sometimes things feel heavy, and it's okay to talk about them.\n"
            "What’s been making today difficult for you?"
        )

# ------------------ Input ------------------
user_input = st.text_input(
    "✍️ Type your thoughts here (English only)",
    placeholder="Example: I feel sad and tired today..."
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
