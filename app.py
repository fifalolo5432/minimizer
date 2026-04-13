import streamlit as st
import tiktoken
import re

# --- CONFIGURATION & DESIGN ---
st.set_page_config(
    page_title="Squeezer. | Minimalist Optimizer",
    page_icon="🤖",
    layout="centered"
)

# Apple-Style CSS Integration
st.markdown("""
    <style>
    .main {
        background-color: #f5f5f7;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    h1 {
        color: #1d1d1f;
        font-weight: 700;
        letter-spacing: -0.05em;
        text-align: center;
        padding-top: 40px;
    }
    .stTextArea textarea {
        border-radius: 12px;
        border: 1px solid #d2d2d7;
        font-size: 16px;
    }
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        background-color: #0071e3;
        color: white;
        border: none;
        padding: 10px 20px;
        font-weight: 500;
    }
    .stButton>button:hover {
        background-color: #0077ed;
        color: white;
    }
    /* Finanz-Karten Styling */
    .cost-card {
        background-color: white;
        padding: 20px;
        border-radius: 18px;
        border: 1px solid #d2d2d7;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
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
    # 1. Instruktions-Lärm & Höflichkeit
    noise = [
        r"\b(helfen|hilf|vorschlagen|schreiben|formuliere|erkläre|erläutere)\b",
        r"\b(möglichst|so wie möglich|bitte|gerne|vielen dank|danke)\b",
        r"ich hoffe es geht dir gut", r"ich würde mich freuen", r"es ist so dass"
    ]
    for pattern in noise:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)

    # 2. Sprach-Check
    if "deutsch" in text.lower():
        text = re.sub(r"\b(auf|in) deutsch\b", "", text, flags=re.IGNORECASE)
        text = text.strip() + " [Sprache: Deutsch]"

    # 3. Partikel-Schnitt (Grammatik-Füllstoffe)
    particles = [
        r"\b(ich|du|dir|mir|mein|meinem|meinen|dich|dein|deine)\b",
        r"\b(der|die|das|ein|eine|einen|dem|den)\b",
        r"\b(an|am|für|zu|in|im|um|da|mit|bei|von|vom)\b"
    ]
    for pattern in particles:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)

    # 4. Struktur & Clean-up
    text = text.replace(" und ", " & ").replace(" oder ", " | ")
    text = re.sub(r"[^a-zA-Z0-9\sÄÖÜäöüß&|\[\]:]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"^(dabei|und|&)\s+", "", text, flags=re.IGNORECASE)
    
    return text.capitalize() if text else ""

# --- UI LAYOUT ---

st.title("Squeezer.")
st.markdown("<p style='text-align: center; color: #86868b; margin-top: -20px;'>Designte Effizienz für deine Prompts.</p>", unsafe_allow_html=True)

model = st.selectbox("Modell wählen", list(LLM_DATA.keys()))

st.markdown("---")
user_input = st.text_area("Originaler Prompt", height=180, placeholder="Text einfügen...")

if user_input:
    optimized = optimize_prompt(user_input)
    t_old = count_tokens(user_input, model)
    t_new = count_tokens(optimized, model)
    
    # Preis-Berechnung
    price_per_1m = LLM_DATA[model]["price"]
    cost_old = (t_old / 1_000_000) * price_per_1m
    cost_new = (t_new / 1_000_000) * price_per_1m
    saving_single = cost_old - cost_new
    saving_1k = saving_single * 1000

    # Anzeige Metriken (Apple-Style Columns)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Tokens gespart", f"{t_old - t_new}", f"-{round(((t_old-t_new)/t_old)*100)}%")
    with c2:
        st.metric("Kosten (Alt)", f"${cost_old:.5f}")
    with c3:
        st.metric("Kosten (Neu)", f"${cost_new:.5f}")

    # Fokus auf die Ersparnis
    st.markdown(f"""
        <div class="cost-card">
            <h3 style="margin:0; color:#86868b; font-size:14px; text-transform:uppercase;">Deine Ersparnis</h3>
            <h1 style="margin:10px 0; color:#0071e3; font-size:48px;">${saving_1k:.3f}</h1>
            <p style="color:#1d1d1f; font-weight:500;">Ersparnis pro 1.000 API-Aufrufen</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("### Optimierter Prompt")
    st.code(optimized, language=None)
    
    st.markdown(f"<p style='text-align:center; font-size:12px; color:#86868b;'>Berechnet auf Basis von {model} Marktpreisen (${price_per_1m}/1M Tokens).</p>", unsafe_allow_html=True)
