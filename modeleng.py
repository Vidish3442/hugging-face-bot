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

# ------------------ DARK THEME + CHAT CSS ------------------
st.markdown(
    """
    <style>
    .stApp {
        background-color: #0f0f0f;
        color: #ffffff;
    }

    h1, h2, h3, h4, h5, h6, p, span, label, small, div {
        color: #ffffff !important;
    }

    .header-card {
        background: #1c1c1c;
        padding: 18px;
        border-radius: 16px;
        text-align: center;
        margin-bottom: 12px;
    }

    .chat-container {
        max-height: 65vh;
        overflow-y: auto;
        padding-right: 6px;
    }

    .user-bubble {
        background: #2e7d32;
        padding: 12px 16px;
        border-radius: 14px;
        margin: 6px 0;
        max-width: 85%;
        margin-left: auto;
        word-wrap: break-word;
    }

    .bot-bubble {
        background: #1f1f1f;
        padding: 12px 16px;
        border-radius: 14px;
        margin: 6px 0;
        max-width: 85%;
        margin-right: auto;
        word-wrap: break-word;
    }

    input[type="text"] {
        background-color: #1c1c1c !important;
        color: #ffffff !important;
        border-radius: 10px;
        border: 1px solid #555;
        font-size: 16px;
    }

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

    @media (max-width: 768px) {
        .chat-container {
            max-height: 60vh;
        }
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

# ------------------ Safety Note (ONCE) ------------------
st.info(
    "🛡️ This chatbot provides emotional support and coping guidance only. "
    "It does not replace professional mental health care."
)

# ------------------ Session State ------------------
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "last_bot_reply" not in st.session_state:
    st.session_state.last_bot_reply = ""

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

# ------------------ Local Fallback (Context-Aware) ------------------
def local_support_response(text):
    text = text.lower()
    last = st.session_state.last_bot_reply.lower()

    if "sad" in text and "sorry" in last:
        return (
            "That makes sense, especially after what you shared earlier.\n\n"
            "Do you want to talk about what’s been weighing on you the most?"
        )

    if "exam" in text:
        return (
            "Bad exams can really affect confidence and mood.\n\n"
            "Was it the preparation, time pressure, or questions that felt hardest?"
        )

    if "sad" in text:
        return (
            "I’m really sorry you’re feeling sad. That can feel heavy.\n\n"
            "What do you think is contributing most to this feeling?"
        )

    return (
        "I’m here with you.\n\n"
        "Tell me more about what’s been going on."
    )

# ------------------ Chat Function ------------------
def chat_with_ai(user_input):

    # Crisis handling
    if crisis_check(user_input):
        return (
            "I’m really glad you told me this. I’m so sorry you’re feeling this much pain.\n\n"
            "You don’t deserve to face this alone. Your life has value.\n\n"
            "📞 India Suicide Helpline: 9152987821\n"
            "🌍 Global: https://findahelpline.com\n\n"
            f"{grounding_exercise()}\n\n"
            "If you can, are you safe right now?"
        )

    # Try OpenRouter
    if client:
        for model in [
            "mistralai/mistral-7b-instruct:free",
            "openchat/openchat-7b:free"
        ]:
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
                if reply:
                    return reply.strip()

            except Exception:
                continue

    return local_support_response(user_input)

# ------------------ CHAT DISPLAY (TOP) ------------------
st.markdown("<div class='chat-container' id='chat'>", unsafe_allow_html=True)

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

st.markdown("</div>", unsafe_allow_html=True)

# ------------------ AUTO SCROLL ------------------
st.markdown(
    """
    <script>
    const chat = document.getElementById("chat");
    if (chat) {
        chat.scrollTop = chat.scrollHeight;
    }
    </script>
    """,
    unsafe_allow_html=True
)

# ------------------ INPUT (BOTTOM) ------------------
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
    st.session_state.last_bot_reply = reply
    st.rerun()
