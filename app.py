import streamlit as st
import tiktoken
import re

# Daten für die Token-Zählung und Preise
LLM_DATA = {
    "GPT-4o": {"enc": "cl100k_base", "price": 5.00},
    "GPT-4o-mini": {"enc": "cl100k_base", "price": 0.15},
    "Claude 3.5 Sonnet": {"enc": "cl100k_base", "price": 3.00},
}

def count_tokens(text, model_name):
    encoding = tiktoken.get_encoding(LLM_DATA[model_name]["enc"])
    return len(encoding.encode(text))

def optimize_prompt(text):
    # 1. Instruktions-Lärm (Wörter über das 'Wie' der Hilfe)
    # Diese Verben beschreiben nur den Akt des Antwortens
    instructional_noise = [
        r"\b(helfen|hilf|vorgeschlagen|vorschlagen|schreiben|schreib|formulieren|formuliere)\b",
        r"\b(möglichst|so wie möglich|so gut wie möglich|bitte|gerne)\b",
        r"\b(zeig|zeige|erklär|erkläre|erläutere)\b"
    ]
    for pattern in instructional_noise:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)

    # 2. Social & Meta Noise (Ganze Phrasen)
    meta_noise = [
        r"ich hoffe es geht dir gut",
        r"ich würde mich freuen",
        r"es ist so dass",
        r"danke für deine bemühungen",
        r"vielen dank", r"danke im voraus", r"danke"
    ]
    for phrase in meta_noise:
        text = re.sub(phrase, "", text, flags=re.IGNORECASE)

    # 3. Sprach-Check (Konsolidierung)
    if "deutsch" in text.lower():
        text = re.sub(r"\b(auf|in) deutsch\b", "", text, flags=re.IGNORECASE)
        text = text.strip() + " [Sprache: Deutsch]"

    # 4. Radikaler Partikel-Schnitt (Die "Kleber-Wörter")
    # Wir löschen Pronomen, Artikel und Präpositionen
    # Diese machen 30% des Token-Verbrauchs aus, ohne Inhalt zu liefern
    particles = [
        r"\b(ich|du|dir|mir|mein|meinem|meinen|dich|dein|deine|euer|ihr)\b",
        r"\b(der|die|das|ein|eine|einen|dem|den|einer|eines)\b",
        r"\b(an|am|für|zu|in|im|um|da|mit|bei|von|vom)\b"
    ]
    for pattern in particles:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)

    # 5. Clean-up & Struktur
    text = text.replace(" und ", " & ").replace(" oder ", " | ")
    # Satzzeichen-Reinigung (löscht alles außer Buchstaben und Zahlen)
    text = re.sub(r"[^a-zA-Z0-9\sÄÖÜäöüß&|\[\]:]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    
    # Ergebnis validieren: Wenn am Anfang "&" oder "Dabei" steht, weg damit
    text = re.sub(r"^(dabei|und|&)\s+", "", text, flags=re.IGNORECASE)
    
    return text.capitalize() if text else ""

st.title("✂️ Mein Token-Minimizer")
model = st.selectbox("Ziel-Modell wählen:", list(LLM_DATA.keys()))
user_input = st.text_area("Originaler Prompt hier rein:", height=150)

if user_input:
    opt_text = optimize_prompt(user_input)
    t_old = count_tokens(user_input, model)
    t_new = count_tokens(opt_text, model)
    
    st.subheader("Optimierter Prompt:")
    st.code(opt_text)
    
    st.write(f"Du sparst **{t_old - t_new} Tokens**.")
