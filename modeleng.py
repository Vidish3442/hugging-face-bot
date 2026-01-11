import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os

# ------------------ Load API Key ------------------
load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")

client = None
if api_key:
    client = OpenAI(
        api_key=api_key,
        base_url="https://openrouter.ai/api/v1"
    )

# ------------------ UI ------------------
st.set_page_config(page_title="🌸 ManoSakhi 🌸", layout="centered")
st.title("🌸 ManoSakhi – Mental Health Chatbot 🌸")
st.markdown("A safe space to talk 🤍")
st.caption("⚠️ Emotional support only. Not a medical professional.")

st.info(
    "🛡️ **Safety Note:** This chatbot provides emotional support and coping guidance only. "
    "It does not replace professional mental health care."
)

# ------------------ Session State ------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "mood" not in st.session_state:
    st.session_state.mood = 5

# ------------------ Mood Slider ------------------
st.markdown("### 🎚️ How are you feeling right now?")
mood = st.slider(
    "1 = Very bad, 10 = Very good",
    min_value=1,
    max_value=10,
    value=st.session_state.mood
)
st.session_state.mood = mood

if mood <= 3:
    st.warning("💙 It looks like you're feeling low. I'm here with you.")
elif mood <= 6:
    st.info("🌤️ Thanks for sharing. Let's talk it out.")
else:
    st.success("🌈 Glad you're feeling okay. I'm here if you want to talk.")

# ------------------ Crisis Check ------------------
def crisis_check(text):
    keywords = [
        "suicide", "kill myself", "end my life",
        "self harm", "cut myself", "die"
    ]
    return any(k in text.lower() for k in keywords)

# ------------------ Grounding Exercise ------------------
def grounding_exercise():
    return (
        "Let’s pause together for a moment.\n\n"
        "🫁 Breathe in slowly for 4 seconds…\n"
        "Hold for 2 seconds…\n"
        "Breathe out gently for 6 seconds.\n\n"
        "Try to notice:\n"
        "• 5 things you can see\n"
        "• 4 things you can feel\n"
        "• 3 things you can hear\n"
        "• 2 things you can smell\n"
        "• 1 thing you can taste\n\n"
        "I’m here with you."
    )

# ------------------ Local Fallback ------------------
def local_support_response(text):
    text = text.lower()

    if "sad" in text:
        return (
            "I’m really sorry you’re feeling sad. That can feel very heavy.\n\n"
            "Do you want to share what’s been causing this feeling?"
        )

    if "lonely" in text:
        return (
            "Feeling lonely can hurt deeply.\n\n"
            "You’re not alone here. What’s been making you feel this way?"
        )

    if "stress" in text or "overwhelmed" in text:
        return (
            "It sounds like a lot has been piling up for you.\n\n"
            "What’s been the most stressful part lately?"
        )

    return (
        "Thank you for sharing that with me.\n\n"
        "I’m here to listen. Tell me more about what’s on your mind."
    )

# ------------------ Chat Function ------------------
def chat_with_ai(user_input):

    # Crisis handling (NO AI)
    if crisis_check(user_input):
        return (
            "I’m really glad you told me this. I’m so sorry you’re feeling this much pain.\n\n"
            "You don’t deserve to face this alone, and your life has value.\n\n"
            "Please consider reaching out to someone right now who can support you.\n\n"
            "📞 **India Suicide Helpline:** 9152987821\n"
            "🌍 **Global:** https://findahelpline.com\n\n"
            f"{grounding_exercise()}\n\n"
            "If you’re able to answer, are you safe right now?"
        )

    # Try OpenRouter
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
                        {
                            "role": "user",
                            "content": (
                                f"My mood today is {st.session_state.mood}/10.\n"
                                f"{user_input}"
                            )
                        }
                    ],
                    timeout=20
                )

                reply = response.choices[0].message.content
                if reply and reply.strip():
                    return reply.strip()

            except Exception:
                continue

    # Always-safe fallback
    return local_support_response(user_input)

# ------------------ Input ------------------
st.markdown("---")
user_input = st.text_input(
    "✍️ Type your thoughts here (English only)",
    placeholder="Example: I feel sad and tired today..."
)

if st.button("Send ✉️") and user_input.strip():
    reply = chat_with_ai(user_input)
    st.session_state.chat_history.append(("user", user_input))
    st.session_state.chat_history.append(("bot", reply))

# ------------------ Display Chat ------------------
for role, msg in st.session_state.chat_history:
    if role == "user":
        st.markdown(f"🧑 **You:** {msg}")
    else:
        st.markdown(f"🤖 **ManoSakhi:** {msg}")
