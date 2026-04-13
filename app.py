import streamlit as st
import tiktoken
import re

# --- CONFIGURATION & DESIGN ---
st.set_page_config(
    page_title="Prompt Squeezer | Minimalist Optimizer",
    page_icon="🤖",
    layout="centered"
)

# Apple-Style CSS Integration
st.markdown("""
    <style>
    /* Hintergrund und Schriftart */
    .main {
        background-color: #f5f5f7;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Titel-Styling */
    h1 {
        color: #1d1d1f;
        font-weight: 700;
        letter-spacing: -0.05em;
        text-align: center;
        padding-bottom: 20px;
    }

    /* Container für die Karten */
    .stTextArea textarea {
        border-radius: 12px;
        border: 1px solid #d2d2d7;
        padding: 15px;
        font-size: 16px;
    }

    /* Button Styling */
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        background-color: #0071e3;
        color: white;
        border: none;
        padding: 10px 20px;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background-color: #0077ed;
        border: none;
        color: white;
        transform: scale(1.02);
    }

    /* Metriken Styling */
    [data-testid="stMetricValue"] {
        font-size: 32px;
        font-weight: 600;
        color: #1d1d1f;
    }

    /* Code-Block Styling */
    .stCodeBlock {
        border-radius: 12px;
        border: 1px solid #d2d2d7;
        background-color: #ffffff !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- LOGIK (LEVEL 1.6) ---

LLM_DATA = {
    "GPT-4o": {"enc": "cl100k_base", "price": 5.00},
    "GPT-4o-mini": {"enc": "cl100k_base", "price": 0.15},
    "Claude 3.5 Sonnet": {"enc": "cl100k_base", "price": 3.00},
}

def count_tokens(text, model_name):
    encoding = tiktoken.get_encoding(LLM_DATA[model_name]["enc"])
    return len(encoding.encode(text))

def optimize_prompt(text):
    # 1. Instruktions-Lärm
    instructional_noise = [
        r"\b(helfen|hilf|vorgeschlagen|vorschlagen|schreiben|schreib|formulieren|formuliere)\b",
        r"\b(möglichst|so wie möglich|so gut wie möglich|bitte|gerne)\b",
        r"\b(zeig|zeige|erklär|erkläre|erläutere)\b"
    ]
    for pattern in instructional_noise:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)

    # 2. Social & Meta Noise
    meta_noise = [
        r"ich hoffe es geht dir gut",
        r"ich würde mich freuen",
        r"es ist so dass",
        r"danke für deine bemühungen",
        r"vielen dank", r"danke im voraus", r"danke"
    ]
    for phrase in meta_noise:
        text = re.sub(phrase, "", text, flags=re.IGNORECASE)

    # 3. Sprach-Check
    if "deutsch" in text.lower():
        text = re.sub(r"\b(auf|in) deutsch\b", "", text, flags=re.IGNORECASE)
        text = text.strip() + " [Sprache: Deutsch]"

    # 4. Radikaler Partikel-Schnitt
    particles = [
        r"\b(ich|du|dir|mir|mein|meinem|meinen|dich|dein|deine|euer|ihr)\b",
        r"\b(der|die|das|ein|eine|einen|dem|den|einer|eines)\b",
        r"\b(an|am|für|zu|in|im|um|da|mit|bei|von|vom)\b"
    ]
    for pattern in particles:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)

    # 5. Clean-up & Struktur
    text = text.replace(" und ", " & ").replace(" oder ", " | ")
    text = re.sub(r"[^a-zA-Z0-9\sÄÖÜäöüß&|\[\]:]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"^(dabei|und|&)\s+", "", text, flags=re.IGNORECASE)
    
    return text.capitalize() if text else ""

# --- UI LAYOUT ---

st.title("Squeezer.")
st.markdown("<p style='text-align: center; color: #86868b;'>Weniger Tokens. Gleiche Brillanz.</p>", unsafe_allow_html=True)

# Modell-Auswahl im Apple-Stil (clean)
model = st.selectbox("Wähle dein LLM", list(LLM_DATA.keys()))

# Input Bereich
st.markdown("---")
user_input = st.text_area("Dein Prompt", height=200, placeholder="Füge hier deinen Text ein...")

if user_input:
    optimized = optimize_prompt(user_input)
    t_old = count_tokens(user_input, model)
    t_new = count_tokens(optimized, model)
    
    # Statistiken in eleganten Karten
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Original", t_old)
    with col2:
        st.metric("Optimiert", t_new, delta=f"-{round(((t_old-t_new)/t_old)*100)}%")
    with col3:
        # Ersparnis bei 1000 Aufrufen
        saving = (t_old - t_new) * (LLM_DATA[model]["price"] / 1_000_000) * 1000
        st.metric("Ersparnis", f"${saving:.3f}")

    # Output Bereich
    st.markdown("### Optimiertes Ergebnis")
    st.code(optimized, language=None)
    
    st.markdown("<p style='font-size: 12px; color: #86868b; text-align: center;'>Optimiert nach Level 1.6 Standards für maximale Effizienz.</p>", unsafe_allow_html=True)
