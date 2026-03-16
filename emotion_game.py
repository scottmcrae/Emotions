import streamlit as st
import random
from PIL import Image, ImageEnhance
import io
import requests
import base64

st.set_page_config(page_title="Emotion Match", page_icon="🎭", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=DM+Sans:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background: #fdf6ee; }
#MainMenu { visibility: hidden; }
header { visibility: hidden; }
footer { visibility: hidden; }
.stAppDeployButton { display: none; }
[data-testid="stToolbar"] { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }
[data-testid="stStatusWidget"] { display: none !important; }

.block-container { padding-top: 1rem !important; padding-bottom: 0 !important; }

.game-title {
    font-family: 'Playfair Display', serif;
    font-size: clamp(1.8rem, 6vw, 2.8rem);
    text-align: left;
    margin: 0 0 0.3rem 0;
    padding-left: 80px;
    letter-spacing: -1px;
    line-height: 1.2;
}
.feedback-correct {
    background: #d4edda; border: 2px solid #28a745; border-radius: 14px;
    padding: 1rem 1.5rem; text-align: center;
    font-size: clamp(1rem, 4vw, 1.4rem); font-weight: 700; color: #155724;
    margin: 0.5rem 0; font-family: 'Playfair Display', serif;
}
.feedback-wrong {
    background: #fff3cd; border: 2px solid #e0a800; border-radius: 14px;
    padding: 0.5rem 1rem; text-align: center;
    font-size: clamp(1rem, 4vw, 1.3rem); font-weight: 600; color: #856404;
    margin: 0.3rem 0 0 0;
}
.btn-row { display: flex; gap: 6px; margin-top: 0.3rem; }
.ans-btn {
    flex: 1;
    font-family: 'DM Sans', sans-serif;
    font-size: clamp(0.9rem, 3vw, 1.1rem);
    font-weight: 600; color: #000;
    background-color: #aaaaaa; border: 2px solid #999;
    border-radius: 10px; padding: 0.2rem 0.3rem;
    cursor: pointer; text-align: center;
}
.ans-btn:hover { background-color: #1a1a2e; color: #fdf6ee; border-color: #1a1a2e; }

/* Next round button */
.stButton > button {
    padding: 0.4rem 1.5rem !important; border-radius: 50px !important;
    font-size: 1rem !important; font-weight: 600 !important;
    background-color: #1a1a2e !important; color: #fdf6ee !important;
    border: none !important;
}
</style>
""", unsafe_allow_html=True)

GITHUB_RAW = "https://raw.githubusercontent.com/scottmcrae/Emotions/main/images"
EMOTIONS = [
    {"label": "Anger",     "emoji": "😠", "image": f"{GITHUB_RAW}/anger1.jpg"},
    {"label": "Contempt",  "emoji": "😒", "image": f"{GITHUB_RAW}/contempt1.jpg"},
    {"label": "Disgust",   "emoji": "🤢", "image": f"{GITHUB_RAW}/disgust1.jpg"},
    {"label": "Happy", "emoji": "😄", "image": f"{GITHUB_RAW}/happy1.jpg"},
    {"label": "Fear",      "emoji": "😨", "image": f"{GITHUB_RAW}/fear1.jpg"},
    {"label": "Sad",       "emoji": "😢", "image": f"{GITHUB_RAW}/sad1.jpg"},
    {"label": "Surprise",  "emoji": "😲", "image": f"{GITHUB_RAW}/surprise1.jpg"},
]

@st.cache_data(show_spinner=False)
def load_image_bytes(url):
    try:
        r = requests.get(url, timeout=8)
        r.raise_for_status()
        return r.content
    except:
        return None

def grey_image(b):
    img = Image.open(io.BytesIO(b)).convert("RGBA")
    dark = ImageEnhance.Brightness(img.convert("L").convert("RGBA")).enhance(0.4)
    buf = io.BytesIO()
    dark.save(buf, format="PNG")
    return buf.getvalue()

def pick_new_round():
    t = random.choice(EMOTIONS)
    opts = random.sample([e for e in EMOTIONS if e["label"] != t["label"]], 3) + [t]
    random.shuffle(opts)
    return t, opts

if "target" not in st.session_state:
    st.session_state.target, st.session_state.options = pick_new_round()
    st.session_state.answered = False
    st.session_state.correct = False
    st.session_state.score = 0
    st.session_state.round = 1
    st.session_state.wrong_attempts = 0

# Handle button clicks via query params
params = st.query_params
if "choice" in params:
    choice = params["choice"]
    st.query_params.clear()
    if choice == st.session_state.target["label"]:
        st.session_state.answered = True
        st.session_state.correct = True
        st.session_state.score += max(3 - st.session_state.wrong_attempts, 1)
    else:
        st.session_state.wrong_attempts += 1
    st.rerun()

target = st.session_state.target
img_bytes = load_image_bytes(target["image"])

# Title
st.markdown(
    '<div class="game-title">'
    '<span style="color:#FF0000">E</span><span style="color:#FF7700">m</span>'
    '<span style="color:#FFD700">o</span><span style="color:#00AA00">t</span>'
    '<span style="color:#0000FF">i</span><span style="color:#4B0082">o</span>'
    '<span style="color:#8B00FF">n</span>&nbsp;'
    '<span style="color:#FF0000">M</span><span style="color:#FF7700">a</span>'
    '<span style="color:#FFD700">t</span><span style="color:#00AA00">c</span>'
    '<span style="color:#0000FF">h</span><span style="color:#1a1a2e">!</span>'
    '</div>',
    unsafe_allow_html=True
)

# Image + buttons in ONE html block — zero Streamlit gap between them
if img_bytes:
    disp = grey_image(img_bytes) if st.session_state.wrong_attempts > 0 and not st.session_state.correct else img_bytes
    b64 = base64.b64encode(disp).decode()
    try_again = '<div class="feedback-wrong">🔄 Try Again</div>' if st.session_state.wrong_attempts > 0 and not st.session_state.correct else ""

    if not (st.session_state.answered and st.session_state.correct):
        opts = st.session_state.options
        btn_html = "".join([
            f'<button class="ans-btn" onclick="window.parent.location.href=window.parent.location.pathname+\'?choice={o["label"]}\'">{o["emoji"]} {o["label"]}</button>'
            for o in opts
        ])
        bottom = f'<div class="btn-row">{btn_html}</div>'
    else:
        bottom = f'<div class="feedback-correct">✅ Correct! That\'s <em>{target["label"]}</em>!</div>'

    st.markdown(
        f'<img style="width:100%;border-radius:16px;display:block;" src="data:image/jpeg;base64,{b64}" />'
        f'{try_again}{bottom}',
        unsafe_allow_html=True
    )
else:
    st.error("⚠️ Image not found.")

# Next round button
if st.session_state.answered and st.session_state.correct:
    col_c = st.columns([1, 2, 1])[1]
    with col_c:
        if st.button("Next Round →"):
            st.session_state.target, st.session_state.options = pick_new_round()
            st.session_state.answered = False
            st.session_state.correct = False
            st.session_state.wrong_attempts = 0
            st.session_state.round += 1
            st.rerun()
