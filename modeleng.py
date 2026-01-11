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

# ------------------ DARK THEME CSS ------------------
st.markdown(
    """
    <style>
    /* App background */
    .stApp {
        background-color: #0f0f0f;
        color: #ffffff !important;
    }

    /* Force light text */
    h1, h2, h3, h4, h5, h6, p, span, label, small, div {
        color: #ffffff !important;
    }

    /* Header card */
    .header-card {
        background: #1c1c1c;
        padding: 18px;
        border-radius: 16px;
        box-shadow: 0px 4px 12px rgba(255,255,255,0.05);
        text-align: center;
        margin-bottom: 16px;
    }

    /* Info box */
    .stAlert {
        background-color: #1e3a5f !important;
        color: #ffffff !important;
        border-radius: 12px;
    }

    /* Chat bubbles */
    .user-bubble {
        background: #2e7d32;
        color: #ffffff;
        padding: 12px 16px;
        border-radius: 14px;
        margin: 8px 0;
        max-width: 85%;
        margin-left: auto;
        box-shadow: 0px 2px 6px rgba(0,0,0,0.5);
    }

    .bot-bubble {
        background: #1f1f1f;
        color: #ffffff;
        padding: 12px 16px;
        border-radius: 14px;
        margin: 8px 0;
        max-width: 85%;
        margin-right: auto;
        box-shadow: 0px 2px 6px rgba(0,0,0,0.5);
    }

    /* Input box */
    input[type="text"] {
        background-color: #1c1c1c !important;
        color: #ffffff !important;
        border-radius: 10px;
        border: 1px solid #555555;
        font-size: 16px;
    }

    /* Send button */
    div.stButton > button {
        background-color: #4CAF50 !important;
        color: white !important;
        padding: 0.6em 1.2em;
        border-radius: 10px;
        font-size: 16px;
        border: none;
    }

    div.stButton > button:hover {
        background-color: #43a047 !important;
    }

    /* Mobile adjustments */
    @media (max-width: 768px) {
        .user-bubble, .bot-bubble {
            max-width: 95%;
            font-size: 15px;
        }
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
        <small>Emotional support only. Not medical advice.</small>
    </div>
    """,
    unsafe_allow_html=True
)

# ------------------ Single Safety Message ------------------
st.info(
    "🛡️ **Safety Note:** This chatbot provides emotional support and coping guidance only. "
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

    if "sad" in text:
        return (
            "I’m really sorry you’re feeling sad. That can feel very heavy.\n\n"
            "Do you want to share what’s been causing this?"
        )

    if "lonely" in text:
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
            "You don’t deserve to face this alone, and your life has value.\n\n"
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

send = st.button("Send ✉️")

if send and user_input.strip():
    reply = chat_with_ai(user_input)
    st.session_state.chat_history.append(("user", user_input))
    st.session_state.chat_history.append(("bot", reply))

# ------------------ Display Chat ------------------
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
