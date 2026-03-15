import streamlit as st
import random
from PIL import Image, ImageEnhance
import io
import requests

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(page_title="Emotion Match", page_icon="🎭", layout="centered")

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=DM+Sans:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
h1, h2, h3 { font-family: 'Playfair Display', serif; }
.stApp { background: #fdf6ee; }

/* Hide Streamlit top bar, menu, and footer */
#MainMenu { visibility: hidden; }
header { visibility: hidden; }
footer { visibility: hidden; }
.stAppDeployButton { display: none; }

/* Responsive image container — fills width on phone, capped on desktop */
[data-testid="stImage"] img {
    width: 100% !important;
    max-width: 960px !important;
    height: auto !important;
    border-radius: 16px;
    display: block;
    margin: 0 auto;
}

.game-title {
    font-family: 'Playfair Display', serif;
    font-size: clamp(1.8rem, 6vw, 2.8rem);
    color: #1a1a2e;
    text-align: center;
    margin-bottom: 0.2rem;
    letter-spacing: -1px;
}
.game-subtitle {
    text-align: center;
    color: #7a7a8c;
    font-size: clamp(0.85rem, 3vw, 1rem);
    margin-bottom: 1.5rem;
}
.score-bar {
    display: flex;
    justify-content: center;
    gap: 1rem;
    margin-bottom: 1.5rem;
    flex-wrap: wrap;
}
.score-chip {
    background: #1a1a2e;
    color: #fdf6ee;
    padding: 10px 14px;
    border-radius: 12px;
    font-size: clamp(0.75rem, 3vw, 0.85rem);
    font-weight: 500;
    letter-spacing: 0.5px;
    text-align: center;
    line-height: 1.5;
    display: block;
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
    margin: 0.75rem 0;
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
    margin: 0.75rem 0;
}

/* Emotion buttons — big tap targets for phones */
div[data-testid="column"] .stButton > button {
    width: 100%;
    padding: clamp(0.8rem, 3vw, 1rem) 0.5rem;
    border-radius: 14px;
    font-size: clamp(1rem, 4vw, 1.15rem);
    font-weight: 600;
    border: 2px solid #d0cfe8;
    background: #ffffff;
    color: #1a1a2e;
    transition: all 0.18s ease;
    cursor: pointer;
    letter-spacing: 0.3px;
    min-height: 56px;
}
div[data-testid="column"] .stButton > button:hover {
    background: #1a1a2e;
    color: #fdf6ee;
    border-color: #1a1a2e;
    transform: translateY(-2px);
    box-shadow: 0 4px 14px rgba(26,26,46,0.15);
}

.round-label {
    text-align: center;
    color: #aaa;
    font-size: 0.75rem;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-bottom: 0.5rem;
}
hr { border: none; border-top: 1px solid #e5e0d8; margin: 1.25rem 0; }
</style>
""", unsafe_allow_html=True)

# ── GitHub raw image base URL ─────────────────────────────────────────────────
GITHUB_RAW = "https://raw.githubusercontent.com/scottmcrae/Emotions/main/images"

# ── Emotion definitions ───────────────────────────────────────────────────────
EMOTIONS = [
    {"label": "Anger",     "emoji": "😠", "image": f"{GITHUB_RAW}/anger1.jpg"},
    {"label": "Contempt",  "emoji": "😒", "image": f"{GITHUB_RAW}/contempt1.jpg"},
    {"label": "Disgust",   "emoji": "🤢", "image": f"{GITHUB_RAW}/disgust1.jpg"},
    {"label": "Enjoyment", "emoji": "😄", "image": f"{GITHUB_RAW}/enjoyment1.jpg"},
    {"label": "Fear",      "emoji": "😨", "image": f"{GITHUB_RAW}/fear1.jpg"},
    {"label": "Sadness",   "emoji": "😢", "image": f"{GITHUB_RAW}/sadness1.jpg"},
    {"label": "Surprise",  "emoji": "😲", "image": f"{GITHUB_RAW}/surprise1.jpg"},
]

# ── Helpers ───────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner=False)
def load_image_bytes(url: str) -> bytes | None:
    try:
        resp = requests.get(url, timeout=8)
        resp.raise_for_status()
        return resp.content
    except Exception as e:
        return None

def grey_image(image_bytes: bytes, brightness: float = 0.4) -> bytes:
    img = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
    grey = img.convert("L").convert("RGBA")
    darkened = ImageEnhance.Brightness(grey).enhance(brightness)
    buf = io.BytesIO()
    darkened.save(buf, format="PNG")
    return buf.getvalue()

def pick_new_round():
    target = random.choice(EMOTIONS)
    distractors = random.sample([e for e in EMOTIONS if e["label"] != target["label"]], 3)
    options = distractors + [target]
    random.shuffle(options)
    return target, options

# ── Session state init ────────────────────────────────────────────────────────
if "target" not in st.session_state:
    st.session_state.target, st.session_state.options = pick_new_round()
    st.session_state.answered = False
    st.session_state.correct = False
    st.session_state.score = 0
    st.session_state.round = 1
    st.session_state.wrong_attempts = 0

# ── UI ────────────────────────────────────────────────────────────────────────
st.markdown('<div class="game-title">🎭 Emotion Match</div>', unsafe_allow_html=True)


target = st.session_state.target

# ── Image + score side by side ────────────────────────────────────────────────
img_bytes = load_image_bytes(target["image"])

img_col, score_col = st.columns([5, 1])

with img_col:
    if img_bytes is None:
        st.error(
            f"⚠️ Could not load `{target['label'].lower()}1.jpg` from GitHub. "
            f"Check that the file exists in your "
            f"[images/ folder](https://github.com/scottmcrae/Emotions/tree/main/images)."
        )
    else:
        if st.session_state.wrong_attempts > 0 and not st.session_state.correct:
            display_bytes = grey_image(img_bytes)
            st.image(display_bytes, use_container_width=True)
            st.markdown('<div class="feedback-wrong">🔄 Try Again</div>', unsafe_allow_html=True)
        else:
            st.image(img_bytes, use_container_width=True)

with score_col:
    st.markdown(f"""
<div style="display:flex; flex-direction:column; gap:12px; padding-left:20px; padding-top:1rem;">
  <span class="score-chip">⭐ Score<br>{st.session_state.score}</span>
  <span class="score-chip">🎯 Round<br>{st.session_state.round}</span>
</div>
""", unsafe_allow_html=True)

# Correct answer feedback
if st.session_state.answered and st.session_state.correct:
    st.markdown(
        f'<div class="feedback-correct">✅ Correct! That\'s <em>{target["label"]}</em>!</div>',
        unsafe_allow_html=True
    )

st.markdown("<hr>", unsafe_allow_html=True)

# ── Answer buttons ────────────────────────────────────────────────────────────
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

# ── Next round button ─────────────────────────────────────────────────────────
if st.session_state.answered and st.session_state.correct:
    col_c = st.columns([1, 2, 1])[1]
    with col_c:
        if st.button("Next Round →", type="primary"):
            st.session_state.target, st.session_state.options = pick_new_round()
            st.session_state.answered = False
            st.session_state.correct = False
            st.session_state.wrong_attempts = 0
            st.session_state.round += 1
            st.rerun()
