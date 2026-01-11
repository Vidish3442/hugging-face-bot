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

# ------------------ Page Config ------------------
st.set_page_config(
    page_title="🌸 ManoSakhi 🌸",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ------------------ Responsive CSS ------------------
st.markdown(
    """
    <style>
    /* App Background */
    .stApp {
        background: linear-gradient(
            rgba(255,255,255,0.92),
            rgba(255,255,255,0.92)
        ),
        url("https://images.unsplash.com/photo-1527137342181-19aab11a8ee8");
        background-size: cover;
        background-attachment: fixed;
    }

    /* Header */
    .header-card {
        background: #ffffffee;
        padding: 20px;
        border-radius: 18px;
        box-shadow: 0px 6px 15px rgba(0,0,0,0.15);
        text-align: center;
        margin-bottom: 15px;
    }

    /* Chat bubbles */
    .user-bubble, .bot-bubble {
        padding: 12px 16px;
        border-radius: 16px;
        margin: 6px 0;
        box-shadow: 0px 2px 6px rgba(0,0,0,0.12);
        word-wrap: break-word;
        font-size: 16px;
        line-height: 1.4;
    }

    .user-bubble {
        background: #DCF8C6;
        margin-left: auto;
        max-width: 80%;
    }

    .bot-bubble {
        background: #F1F0F0;
        margin-right: auto;
        max-width: 80%;
    }

    /* Mobile optimization */
    @media (max-width: 768px) {
        .header-card {
            padding: 14px;
        }

        .user-bubble, .bot-bubble {
            font-size: 15px;
            max-width: 95%;
        }
    }

    /* Input box spacing */
    input[type="text"] {
        font-size: 16px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ------------------ Header ------------------
st.markdown(
    """
    <div class="header-card">
        <h2>🌸 ManoSakhi</h2>
        <p><b>Mental Health Chatbot</b></p>
        <p>A safe space to talk 🤍</p>
        <small>⚠️ Emotional support only. Not medical advice.</small>
    </div>
    """,
    unsafe_allow_html=True
)

st.info(
    "🛡️ This chatbot offers emotional support and coping guidance only. "
    "It does not replace professional mental health care."
)

# ------------------ Session State ------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

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
        "Notice:\n"
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

    if "sad" in text or "down" in text:
        return (
            "I’m really sorry you’re feeling sad. That can feel heavy.\n\n"
            "Do you want to share what’s been causing this?"
        )

    if "lonely" in text or "alone" in text:
        return (
            "Feeling lonely can hurt deeply.\n\n"
            "You’re not alone here. What’s been making you feel this way?"
        )

    if "stress" in text or "overwhelmed" in text:
        return (
            "It sounds like a lot has been piling up.\n\n"
            "What’s been the most stressful part?"
        )

    return (
        "Thank you for sharing.\n\n"
        "I’m here to listen. Tell me more."
    )

# ------------------ Chat Function ------------------
def chat_with_ai(user_input):

    # Crisis handling
    if crisis_check(user_input):
        return (
            "I’m really glad you told me this. I’m so sorry you’re feeling this much pain.\n\n"
            "You don’t deserve to face this alone. Your life has value.\n\n"
            "📞 **India Suicide Helpline:** 9152987821\n"
            "🌍 **Global:** https://findahelpline.com\n\n"
            f"{grounding_exercise()}\n\n"
            "If you can, are you safe right now?"
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
                        {"role": "user", "content": user_input}
                    ],
                    timeout=20
                )

                reply = response.choices[0].message.content
                if reply and reply.strip():
                    return reply.strip()

            except Exception:
                continue

    return local_support_response(user_input)

# ------------------ Input ------------------
st.markdown("---")
user_input = st.text_input(
    "✍️ Type your thoughts here (English only)",
    placeholder="Example: I feel sad today..."
)

if st.button("Send ✉️") and user_input.strip():
    reply = chat_with_ai(user_input)
    st.session_state.chat_history.append(("user", user_input))
    st.session_state.chat_history.append(("bot", reply))

# ------------------ Chat Display ------------------
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
