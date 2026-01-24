import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os
import datetime
import random

# ================= LOAD API KEYS =================
load_dotenv()
openrouter_key = os.getenv("OPENROUTER_API_KEY")
huggingface_key = os.getenv("HUGGINGFACE_API_KEY")

openrouter_client = None
if openrouter_key:
    openrouter_client = OpenAI(
        api_key=openrouter_key,
        base_url="https://openrouter.ai/api/v1"
    )

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="🌸 ManoSakhi - Mental Health Support",
    page_icon="🌸",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ================= UI STYLE =================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #0f0f0f, #1a1a1a);
    color: white;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}
.header-card {
    background: linear-gradient(135deg, #2c2c2c, #1f1f1f);
    padding: 24px;
    border-radius: 20px;
    text-align: center;
    margin-bottom: 20px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    border: 1px solid rgba(255, 255, 255, 0.1);
}
.user-bubble {
    background: linear-gradient(135deg, #2e7d32, #388e3c);
    padding: 16px 20px;
    border-radius: 18px;
    margin: 12px 0;
    max-width: 85%;
    margin-left: auto;
    box-shadow: 0 4px 16px rgba(46, 125, 50, 0.3);
    border: 1px solid rgba(255, 255, 255, 0.1);
}
.bot-bubble {
    background: linear-gradient(135deg, #2c2c2c, #1e1e1e);
    padding: 16px 20px;
    border-radius: 18px;
    margin: 12px 0;
    max-width: 85%;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
    border: 1px solid rgba(255, 255, 255, 0.1);
}
.resource-card {
    background: linear-gradient(135deg, #6a1b9a, #4a148c);
    padding: 16px;
    border-radius: 12px;
    margin: 12px 0;
    box-shadow: 0 4px 16px rgba(106, 27, 154, 0.3);
    border: 1px solid rgba(255, 255, 255, 0.1);
}
.stTextArea > div > div > textarea {
    background-color: #2c2c2c;
    color: white;
    border: 2px solid #444;
    border-radius: 12px;
    padding: 12px;
}
.stButton > button {
    background: linear-gradient(135deg, #2e7d32, #388e3c);
    color: white;
    border: none;
    border-radius: 12px;
    padding: 12px 24px;
    font-weight: 600;
    transition: all 0.3s ease;
}
</style>
""", unsafe_allow_html=True)

# ================= HEADER =================
st.markdown("""
<div class="header-card">
<h1>🌸 ManoSakhi</h1>
<h3>Your Compassionate Mental Health Companion</h3>
<p>A safe, judgment-free space to share your thoughts and feelings 🤍</p>
<small>⚠️ For emotional support only • Not a substitute for professional medical care</small>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="resource-card">
<h4>🆘 Crisis Resources (Available 24/7)</h4>
<p><strong>India:</strong> 📞 9152987821 (AASRA) | 📞 1860-2662-345 (iCall)</p>
<p><strong>International:</strong> 🌍 <a href="https://findahelpline.com" target="_blank">findahelpline.com</a></p>
</div>
""", unsafe_allow_html=True)

# ================= SESSION STATE =================
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "last_bot_reply" not in st.session_state:
    st.session_state.last_bot_reply = ""

# ================= MODELS =================
MODELS = [
    "meta-llama/llama-3.2-3b-instruct:free",
    "microsoft/phi-3-mini-128k-instruct:free",
    "google/gemma-2-9b-it:free",
    "mistralai/mistral-7b-instruct:free",
    "openchat/openchat-7b:free"
]

# ================= SYSTEM PROMPT =================
SYSTEM_PROMPT = """
You are ManoSakhi, a compassionate mental health support companion. 

IMPORTANT: You must respond naturally and specifically to what the user is sharing. DO NOT use generic phrases.

APPROACH:
- Listen to their specific situation and reflect it back
- Validate their emotions with genuine understanding
- Ask one thoughtful question to help them explore deeper

EXAMPLE:
User: "I think I might fail my exam"
Good response: "The fear of failing when you've been working hard must feel overwhelming. It's that terrible uncertainty - not knowing if your efforts will be enough. What subject is this exam in, and what's making you feel most unprepared?"

Bad response: "That sounds difficult. I'm here for you. How are you feeling?"

Be conversational, caring, and specific to their situation. Keep responses 2-3 sentences.
"""

# ================= CRISIS CHECK =================
def crisis_check(text):
    crisis_keywords = [
        "suicide", "kill myself", "end my life", "want to die",
        "self harm", "cut myself", "hurt myself", "overdose",
        "jump off", "hang myself", "can't go on", "better off dead"
    ]
    
    violence_keywords = [
        "being beaten", "hit me", "abuse", "violence", "hurt me",
        "threatening me", "scared for my life", "domestic violence"
    ]
    
    text_lower = text.lower()
    
    return {
        "crisis": any(keyword in text_lower for keyword in crisis_keywords),
        "violence": any(keyword in text_lower for keyword in violence_keywords)
    }

# ================= GROUNDING EXERCISES =================
def get_grounding_exercise():
    exercises = [
        {
            "name": "5-4-3-2-1 Technique",
            "content": (
                "Let's ground ourselves together 🌱\n\n"
                "Look around and name:\n"
                "👀 5 things you can see\n"
                "👂 4 things you can hear\n"
                "✋ 3 things you can touch\n"
                "👃 2 things you can smell\n"
                "👅 1 thing you can taste\n\n"
                "Take your time. You're safe right now."
            )
        },
        {
            "name": "Box Breathing",
            "content": (
                "Let's breathe together 🫁\n\n"
                "Breathe in slowly for 4 counts... 1, 2, 3, 4\n"
                "Hold for 4 counts... 1, 2, 3, 4\n"
                "Breathe out for 4 counts... 1, 2, 3, 4\n"
                "Hold for 4 counts... 1, 2, 3, 4\n\n"
                "Repeat this cycle. You're doing great."
            )
        }
    ]
    return random.choice(exercises)



# ================= INTELLIGENT FALLBACK =================
def get_intelligent_fallback(user_input):
    """Generate intelligent fallback responses based on user input analysis"""
    user_lower = user_input.lower()
    
    if any(word in user_lower for word in ["sad", "depressed", "down", "crying"]):
        responses = [
            "This sadness feels really overwhelming right now. When everything feels this heavy, it's hard to see past the pain. What's been the hardest part of your day today?",
            "That deep sadness sounds exhausting to carry around. It's like a weight that makes everything else harder. What do you think triggered these feelings?",
            "Feeling this low is really difficult, especially when it seems like it won't lift. The sadness feels so real and consuming. What usually helps you feel even a tiny bit better?"
        ]
        return random.choice(responses)
    
    elif any(word in user_lower for word in ["anxious", "worried", "scared", "panic"]):
        responses = [
            "That anxiety sounds really intense and overwhelming. When your mind races like this, it's exhausting. What thoughts keep coming back that worry you most?",
            "The worry feels so consuming and real, doesn't it? Anxiety can make everything feel urgent and scary. What situation is making you feel most anxious right now?",
            "That anxious feeling in your chest and mind must be really uncomfortable. It's like your thoughts won't slow down. What's the main thing you're worried might happen?"
        ]
        return random.choice(responses)
    
    elif any(word in user_lower for word in ["exam", "test", "fail", "grade", "study"]):
        responses = [
            "The pressure around exams can feel crushing, especially when so much seems to depend on the results. That fear of failing is really scary. What subject is causing you the most stress?",
            "Academic stress hits different because it feels like your whole future depends on it. The fear of disappointing yourself or others is overwhelming. What's making this exam feel so high-stakes for you?",
            "Exam anxiety is so real - that knot in your stomach about potentially failing. It's hard to focus when you're this worried. What part of the exam preparation is stressing you out most?"
        ]
        return random.choice(responses)
    
    elif any(word in user_lower for word in ["friend", "relationship", "fight", "argument"]):
        responses = [
            "Relationship conflicts hurt so much because these people matter to you. When someone important is upset with you, it affects everything. What happened between you two?",
            "Fighting with someone you care about feels awful - that mix of anger, hurt, and worry about the relationship. It's hard to focus on anything else. What started this conflict?",
            "The tension with your friend must be really painful. These relationships mean so much, so when things go wrong, it hits hard. Have you two talked since the argument?"
        ]
        return random.choice(responses)
    
    else:
        responses = [
            "What you're going through sounds really challenging and emotionally draining. It takes courage to reach out when you're struggling. What's been weighing on your mind the most?",
            "This situation sounds genuinely difficult and complex. When we're dealing with something this hard, it affects everything else too. What part of this feels most overwhelming right now?",
            "That sounds like a lot to handle, and it makes sense that you'd be feeling stressed about it. These kinds of situations are never easy. What's your biggest concern about all this?"
        ]
        return random.choice(responses)

# ================= MAIN CHAT FUNCTION =================
def chat_with_ai(user_input):
    # Crisis detection first
    crisis_result = crisis_check(user_input)
    
    if crisis_result["crisis"] or crisis_result["violence"]:
        crisis_response = "I'm really glad you trusted me with this. You're incredibly brave for sharing.\n\n"
        
        if crisis_result["crisis"]:
            crisis_response += (
                "🆘 **Immediate Help Available:**\n"
                "📞 India: 9152987821 (AASRA) | 1860-2662-345 (iCall)\n"
                "🌍 International: https://findahelpline.com\n\n"
            )
        
        if crisis_result["violence"]:
            crisis_response += (
                "🛡️ **Safety Resources:**\n"
                "📞 Women Helpline: 1091 | Domestic Violence: 181\n\n"
            )
        
        # Add grounding exercise
        exercise = get_grounding_exercise()
        crisis_response += f"**{exercise['name']}**\n{exercise['content']}"
        
        return crisis_response
    
    # Build conversation context
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    # Add conversation history
    for role, msg in st.session_state.chat_history[-6:]:
        messages.append({
            "role": "assistant" if role == "bot" else "user",
            "content": msg
        })
    
    messages.append({"role": "user", "content": user_input})
    
    # Try OpenRouter models
    if openrouter_client:
        for model in MODELS:
            try:
                response = openrouter_client.chat.completions.create(
                    model=model,
                    messages=messages,
                    timeout=30,
                    max_tokens=250,
                    temperature=0.7
                )
                
                reply = response.choices[0].message.content.strip()
                
                # Always return AI response if it exists and is not empty
                if reply and len(reply.strip()) > 10:
                    # Avoid repetition
                    if reply != st.session_state.last_bot_reply:
                        return reply
                    else:
                        # If same as last reply, try next model
                        continue
                        
            except Exception as e:
                # Try next model
                continue
    
    # Only use fallback if all AI models fail
    return get_intelligent_fallback(user_input)

# ================= SIDEBAR =================
with st.sidebar:
    st.markdown("### 🌸 ManoSakhi Tools")
    
    if st.button("🧘‍♀️ Quick Grounding Exercise"):
        exercise = get_grounding_exercise()
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #1565c0, #0d47a1); padding: 16px; border-radius: 12px; margin: 8px 0; color: white;">
        <h4>{exercise['name']}</h4>
        <p>{exercise['content']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    if st.session_state.chat_history:
        st.markdown(f"**Messages:** {len(st.session_state.chat_history)}")

# ================= CHAT DISPLAY =================
for role, msg in st.session_state.chat_history:
    if role == "user":
        st.markdown(f"<div class='user-bubble'>� <b>You</b><br>{msg}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='bot-bubble'>🤖 <b>ManoSakhi</b><br>{msg}</div>", unsafe_allow_html=True)

# ================= INPUT SECTION =================
st.markdown("---")

# Text input
user_input = st.text_area(
    "✍️ Share what's on your mind…", 
    placeholder="Type your thoughts here. I'm here to listen without judgment.",
    height=100
)

col1, col2 = st.columns([4, 1])
with col1:
    send = st.button("Send Message 💬", type="primary")
with col2:
    if st.session_state.chat_history:
        clear = st.button("Clear 🗑️")
        if clear:
            st.session_state.chat_history = []
            st.session_state.last_bot_reply = ""
            st.rerun()

if send and user_input.strip():
    reply = chat_with_ai(user_input)
    st.session_state.chat_history.append(("user", user_input))
    st.session_state.chat_history.append(("bot", reply))
    st.session_state.last_bot_reply = reply
    st.rerun()