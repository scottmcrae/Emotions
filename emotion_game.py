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
    margin: 0;
}

.game-title {
    font-family: 'Playfair Display', serif;
    font-size: clamp(1.8rem, 6vw, 2.8rem);
    text-align: center;
    margin: 0 0 2rem -80px;
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

/* Answer button grid — always 2x2, never stacks */
.btn-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
    margin-top: 0.1rem;
}
.ans-btn {
    font-family: 'DM Sans', sans-serif;
    font-size: clamp(1rem, 3.5vw, 1.2rem);
    font-weight: 600;
    color: #000000;
    background-color: #aaaaaa;
    border: 2px solid #999999;
    border-radius: 10px;
    padding: 0.4rem 0.5rem;
    cursor: pointer;
    width: 100%;
    text-align: center;
    transition: all 0.18s ease;
}
.ans-btn:hover {
    background-color: #1a1a2e;
    color: #fdf6ee;
    border-color: #1a1a2e;
    transform: translateY(-2px);
    box-shadow: 0 4px 14px rgba(26,26,46,0.15);
}

/* Next round button */
.stButton > button {
    border-radius: 50px !important;
    background-color: #1a1a2e !important;
    color: #fdf6ee !important;
    border: none !important;
    padding: 0.5rem 2rem !important;
    font-size: 1rem !important;
    font-weight: 600 !important;
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

# Title + image
pad_left, img_col, pad_col = st.columns([0.3, 3, 1])
with img_col:
    st.markdown("""
<div class="game-title"><span style="color:#FF0000">E</span><span style="color:#FF7700">m</span><span style="color:#FFD700">o</span><span style="color:#00AA00">t</span><span style="color:#0000FF">i</span><span style="color:#4B0082">o</span><span style="color:#8B00FF">n</span>&nbsp;<span style="color:#FF0000">M</span><span style="color:#FF7700">a</span><span style="color:#FFD700">t</span><span style="color:#00AA00">c</span><span style="color:#0000FF">h</span><span style="color:#1a1a2e">!</span></div>
""", unsafe_allow_html=True)
    if img_bytes is None:
        st.error("⚠️ Image not found. Check your [GitHub repo](https://github.com/scottmcrae/Emotions/tree/main/images).")
    else:
        if st.session_state.wrong_attempts > 0 and not st.session_state.correct:
            st.image(grey_image(img_bytes), use_container_width=True)
            st.markdown('<div class="feedback-wrong">🔄 Try Again</div>', unsafe_allow_html=True)
        else:
            st.image(img_bytes, use_container_width=True)

if st.session_state.answered and st.session_state.correct:
    st.markdown(f'<div class="feedback-correct">✅ Correct! That\'s <em>{target["label"]}</em>!</div>', unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# Buttons as pure HTML grid — always 2x2 on all screen sizes
if not (st.session_state.answered and st.session_state.correct):
    opts = st.session_state.options
    clicked = st.markdown(f"""
<div class="btn-grid">
  <button class="ans-btn" onclick="window.location.href='?choice={opts[0]['label']}'">{opts[0]['emoji']} {opts[0]['label']}</button>
  <button class="ans-btn" onclick="window.location.href='?choice={opts[1]['label']}'"> {opts[1]['emoji']} {opts[1]['label']}</button>
  <button class="ans-btn" onclick="window.location.href='?choice={opts[2]['label']}'"> {opts[2]['emoji']} {opts[2]['label']}</button>
  <button class="ans-btn" onclick="window.location.href='?choice={opts[3]['label']}'"> {opts[3]['emoji']} {opts[3]['label']}</button>
</div>
""", unsafe_allow_html=True)

    # Detect click via query params
    params = st.query_params
    if "choice" in params:
        choice = params["choice"]
        st.query_params.clear()
        if choice == target["label"]:
            st.session_state.answered = True
            st.session_state.correct = True
            st.session_state.score += max(3 - st.session_state.wrong_attempts, 1)
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
