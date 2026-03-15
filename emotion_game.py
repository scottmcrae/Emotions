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

.block-container {
    padding-top: 2rem !important;
    padding-bottom: 0 !important;
}

[data-testid="stVerticalBlock"] { gap: 0 !important; }
div[data-testid="element-container"] { margin: 0 !important; padding: 0 !important; }
.stMarkdown { margin: 0 !important; padding: 0 !important; }

[data-testid="stImage"] img {
    width: 100% !important;
    height: auto !important;
    border-radius: 16px;
    display: block;
    margin: 0 auto;
}

.game-title {
    font-family: 'Playfair Display', serif;
    font-size: clamp(1.8rem, 6vw, 2.8rem);
    text-align: center;
    margin: 0 0 0.5rem 0;
    padding: 0;
    letter-spacing: -1px;
    line-height: 1.2;
}
.feedback-correct {
    background: #d4edda;
    border: 2px solid #28a745;
    border-radius: 14px;
    padding: 1rem 1.5rem;
    text-align: center;
    font-size: clamp(1rem, 4vw, 1.4rem);
    font-weight: 700;
    color: #155724;
    margin: 0.5rem 0;
    font-family: 'Playfair Display', serif;
}
.feedback-wrong {
    background: #fff3cd;
    border: 2px solid #e0a800;
    border-radius: 14px;
    padding: 1rem 1.5rem;
    text-align: center;
    font-size: clamp(1rem, 4vw, 1.3rem);
    font-weight: 600;
    color: #856404;
    margin: 0.5rem 0 0 0;
}

/* Answer buttons */
.stButton > button {
    padding: 0.3rem 1rem !important;
    border-radius: 10px !important;
    font-size: clamp(1rem, 3.5vw, 1.2rem) !important;
    font-weight: 600 !important;
    border: 2px solid #999999 !important;
    background-color: #aaaaaa !important;
    color: #000000 !important;
    transition: all 0.18s ease;
    cursor: pointer;
    margin-bottom: 6px !important;
}
.stButton > button:hover {
    background-color: #1a1a2e !important;
    color: #fdf6ee !important;
    border-color: #1a1a2e !important;
}

hr { border: none; border-top: 1px solid #e5e0d8; margin: 0.1rem 0; }
</style>
""", unsafe_allow_html=True)

GITHUB_RAW = "https://raw.githubusercontent.com/scottmcrae/Emotions/main/images"
EMOTIONS = [
    {"label": "Anger",     "emoji": "😠", "image": f"{GITHUB_RAW}/anger1.jpg"},
    {"label": "Contempt",  "emoji": "😒", "image": f"{GITHUB_RAW}/contempt1.jpg"},
    {"label": "Disgust",   "emoji": "🤢", "image": f"{GITHUB_RAW}/disgust1.jpg"},
    {"label": "Enjoyment", "emoji": "😄", "image": f"{GITHUB_RAW}/enjoyment1.jpg"},
    {"label": "Fear",      "emoji": "😨", "image": f"{GITHUB_RAW}/fear1.jpg"},
    {"label": "Sadness",   "emoji": "😢", "image": f"{GITHUB_RAW}/sadness1.jpg"},
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

target = st.session_state.target
img_bytes = load_image_bytes(target["image"])

# Title + image in ONE block so they share the same alignment
import base64 as _b64
if img_bytes is None:
    img_html = '<p style="color:red">⚠️ Image not found.</p>'
    try_again_html = ""
else:
    if st.session_state.wrong_attempts > 0 and not st.session_state.correct:
        disp = grey_image(img_bytes)
        try_again_html = '<div class="feedback-wrong">🔄 Try Again</div>'
    else:
        disp = img_bytes
        try_again_html = ""
    b64 = _b64.b64encode(disp).decode()
    img_html = f'<img style="width:100%;border-radius:16px;display:block;" src="data:image/jpeg;base64,{b64}" />'

st.markdown(f'''<div style="text-align:center;">
<div class="game-title"><span style="color:#FF0000">E</span><span style="color:#FF7700">m</span><span style="color:#FFD700">o</span><span style="color:#00AA00">t</span><span style="color:#0000FF">i</span><span style="color:#4B0082">o</span><span style="color:#8B00FF">n</span>&nbsp;<span style="color:#FF0000">M</span><span style="color:#FF7700">a</span><span style="color:#FFD700">t</span><span style="color:#00AA00">c</span><span style="color:#0000FF">h</span><span style="color:#1a1a2e">!</span></div>
{img_html}{try_again_html}
</div>''', unsafe_allow_html=True)

if st.session_state.answered and st.session_state.correct:
    st.markdown(f'<div class="feedback-correct">✅ Correct! That\'s <em>{target["label"]}</em>!</div>', unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

if not (st.session_state.answered and st.session_state.correct):
    cols = st.columns(2)
    for i, option in enumerate(st.session_state.options):
        with cols[i % 2]:
            if st.button(f"{option['emoji']}  {option['label']}", key=f"opt_{i}"):
                if option["label"] == target["label"]:
                    st.session_state.answered = True
                    st.session_state.correct = True
                    st.session_state.score += max(3 - st.session_state.wrong_attempts, 1)
                    st.rerun()
                else:
                    st.session_state.wrong_attempts += 1
                    st.rerun()

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
