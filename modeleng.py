import streamlit as st
from huggingface_hub import InferenceClient
from dotenv import load_dotenv
import os

# ------------------ Load API Key ------------------
load_dotenv()
api_key = os.getenv("HUGGINGFACE_API_KEY")

if not api_key:
    st.error("HUGGINGFACE_API_KEY not found in .env file")
    st.stop()

# ------------------ Hugging Face Client ------------------
client = InferenceClient(
    model="OpenAssistant/oasst-sft-4-pythia-12b",
    token=api_key
)

# ------------------ UI ------------------
st.set_page_config(page_title="🌸 ManoSakhi 🌸")
st.title("🌸 ManoSakhi – Mental Health Chatbot 🌸")
st.subheader("A safe space to talk 🤍")

st.markdown(
    "⚠️ *This chatbot provides emotional support only and is not a medical professional.*"
)

# ------------------ Session ------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# ------------------ Crisis Check ------------------
def crisis_check(text):
    keywords = [
        "suicide", "kill myself", "end my life",
        "self harm", "cut myself", "die"
    ]
    return any(k in text.lower() for k in keywords)

# ------------------ Chat Function ------------------
def chat_with_ai(user_input):

    # Crisis response (NO API call)
    if crisis_check(user_input):
        return (
            "I'm really glad you reached out. What you're feeling matters.\n\n"
            "Please consider speaking to a trusted person or professional right now.\n\n"
            "📞 **India Helpline:** 9152987821\n"
            "🌍 **Global:** https://findahelpline.com\n\n"
            "You are not alone."
        )

    prompt = (
        "You are a kind, empathetic mental health support chatbot.\n"
        "Respond only in simple, supportive English.\n"
        "Do not give medical advice.\n\n"
        f"User: {user_input}\n"
        "Assistant:"
    )

    try:
        response = client.text_generation(
            prompt,
            max_new_tokens=150,
            temperature=0.7,
            top_p=0.9
        )
        return response.strip()

    except Exception:
        return (
            "I'm here with you, but I'm having trouble responding right now. "
            "Please try again in a moment."
        )

# ------------------ Input ------------------
user_input = st.text_input(
    "✍️ Type your thoughts here (English only)",
    placeholder="Example: I feel overwhelmed today..."
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
