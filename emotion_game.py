import streamlit as st
import random
from PIL import Image, ImageEnhance
import io
import requests

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(page_title="Emotion Match", page_icon="🎭", layout="centered")

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=DM+Sans:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

h1, h2, h3 {
    font-family: 'Playfair Display', serif;
}

.stApp {
    background: #fdf6ee;
}

/* Title */
.game-title {
    font-family: 'Playfair Display', serif;
    font-size: 2.8rem;
    color: #1a1a2e;
    text-align: center;
    margin-bottom: 0.2rem;
    letter-spacing: -1px;
}

.game-subtitle {
    text-align: center;
    color: #7a7a8c;
    font-size: 1rem;
    margin-bottom: 2rem;
}

/* Score badge */
.score-bar {
    display: flex;
    justify-content: center;
    gap: 2rem;
    margin-bottom: 1.5rem;
}

.score-chip {
    background: #1a1a2e;
    color: #fdf6ee;
    padding: 6px 20px;
    border-radius: 50px;
    font-size: 0.85rem;
    font-weight: 500;
    letter-spacing: 0.5px;
}

/* Image container */
.img-wrapper {
    position: relative;
    text-align: center;
    margin-bottom: 1.5rem;
}

/* Feedback overlay */
.feedback-correct {
    background: #d4edda;
    border: 2px solid #28a745;
    border-radius: 14px;
    padding: 1rem 1.5rem;
    text-align: center;
    font-size: 1.4rem;
    font-weight: 700;
    color: #155724;
    margin-bottom: 1rem;
    font-family: 'Playfair Display', serif;
}

.feedback-wrong {
    background: #fff3cd;
    border: 2px solid #e0a800;
    border-radius: 14px;
    padding: 1rem 1.5rem;
    text-align: center;
    font-size: 1.3rem;
    font-weight: 600;
    color: #856404;
    margin-bottom: 1rem;
    letter-spacing: 0.5px;
}

/* Emotion buttons */
div[data-testid="column"] .stButton > button {
    width: 100%;
    padding: 0.7rem 0.5rem;
    border-radius: 12px;
    font-size: 1rem;
    font-weight: 500;
    border: 2px solid #d0cfe8;
    background: #ffffff;
    color: #1a1a2e;
    transition: all 0.18s ease;
    cursor: pointer;
    letter-spacing: 0.3px;
}

div[data-testid="column"] .stButton > button:hover {
    background: #1a1a2e;
    color: #fdf6ee;
    border-color: #1a1a2e;
    transform: translateY(-2px);
    box-shadow: 0 4px 14px rgba(26,26,46,0.15);
}

/* Next button */
.stButton > button[kind="primary"] {
    background: #1a1a2e !important;
    color: #fdf6ee !important;
    border: none !important;
    border-radius: 50px !important;
    padding: 0.7rem 2.5rem !important;
    font-size: 1rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.5px;
}

/* Round label */
.round-label {
    text-align: center;
    color: #aaa;
    font-size: 0.8rem;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-bottom: 0.5rem;
}

/* Divider */
hr {
    border: none;
    border-top: 1px solid #e5e0d8;
    margin: 1.5rem 0;
}
</style>
""", unsafe_allow_html=True)

# ── Emotion data (emoji face images via placeholders + labels) ────────────────
# Uses real expressive face emoji as image URLs from a CDN
EMOTIONS = [
    {
        "label": "Happy",
        "emoji": "😄",
        "image_url": "https://em-content.zobj.net/source/apple/354/grinning-face-with-big-eyes_1f603.png",
    },
    {
        "label": "Sad",
        "emoji": "😢",
        "image_url": "https://em-content.zobj.net/source/apple/354/crying-face_1f622.png",
    },
    {
        "label": "Angry",
        "emoji": "😠",
        "image_url": "https://em-content.zobj.net/source/apple/354/angry-face_1f620.png",
    },
    {
        "label": "Surprised",
        "emoji": "😲",
        "image_url": "https://em-content.zobj.net/source/apple/354/astonished-face_1f632.png",
    },
    {
        "label": "Disgusted",
        "emoji": "🤢",
        "image_url": "https://em-content.zobj.net/source/apple/354/nauseated-face_1f922.png",
    },
    {
        "label": "Fearful",
        "emoji": "😨",
        "image_url": "https://em-content.zobj.net/source/apple/354/fearful-face_1f628.png",
    },
    {
        "label": "Confused",
        "emoji": "😕",
        "image_url": "https://em-content.zobj.net/source/apple/354/confused-face_1f615.png",
    },
    {
        "label": "Excited",
        "emoji": "🤩",
        "image_url": "https://em-content.zobj.net/source/apple/354/star-struck_1f929.png",
    },
]

# ── Session state init ────────────────────────────────────────────────────────
def pick_new_round():
    target = random.choice(EMOTIONS)
    distractors = random.sample([e for e in EMOTIONS if e["label"] != target["label"]], 3)
    options = distractors + [target]
    random.shuffle(options)
    return target, options

if "target" not in st.session_state:
    st.session_state.target, st.session_state.options = pick_new_round()
    st.session_state.answered = False
    st.session_state.correct = False
    st.session_state.score = 0
    st.session_state.round = 1
    st.session_state.wrong_attempts = 0

# ── Helpers ───────────────────────────────────────────────────────────────────
def grey_image_from_url(url: str, factor: float = 0.35) -> bytes:
    """Download image, desaturate + darken it, return PNG bytes."""
    resp = requests.get(url, timeout=5)
    img = Image.open(io.BytesIO(resp.content)).convert("RGBA")
    grey = img.convert("L").convert("RGBA")
    darkened = ImageEnhance.Brightness(grey).enhance(factor)
    buf = io.BytesIO()
    darkened.save(buf, format="PNG")
    return buf.getvalue()

@st.cache_data
def load_image_bytes(url: str) -> bytes:
    resp = requests.get(url, timeout=5)
    return resp.content

# ── UI ────────────────────────────────────────────────────────────────────────
st.markdown('<div class="game-title">🎭 Emotion Match</div>', unsafe_allow_html=True)
st.markdown('<div class="game-subtitle">What emotion does this face express?</div>', unsafe_allow_html=True)

# Score bar
st.markdown(f"""
<div class="score-bar">
  <span class="score-chip">⭐ Score: {st.session_state.score}</span>
  <span class="score-chip">🎯 Round: {st.session_state.round}</span>
</div>
""", unsafe_allow_html=True)

st.markdown(f'<div class="round-label">identify the emotion</div>', unsafe_allow_html=True)

# Image display
target = st.session_state.target
if st.session_state.answered and st.session_state.correct:
    img_bytes = load_image_bytes(target["image_url"])
    st.image(img_bytes, width=220, use_container_width=False)
elif st.session_state.wrong_attempts > 0:
    greyed = grey_image_from_url(target["image_url"], factor=0.4)
    st.image(greyed, width=220, use_container_width=False)
    st.markdown('<div class="feedback-wrong">🔄 Try Again</div>', unsafe_allow_html=True)
else:
    img_bytes = load_image_bytes(target["image_url"])
    st.image(img_bytes, width=220, use_container_width=False)

# Feedback on correct
if st.session_state.answered and st.session_state.correct:
    st.markdown(f'<div class="feedback-correct">✅ Correct! That\'s <em>{target["label"]}</em> {target["emoji"]}</div>', unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# Answer buttons (2x2 grid)
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

# Next round button
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
