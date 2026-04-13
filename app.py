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
    # --- EBENE 1: Universelle Füllfloskeln (Social Noise) ---
    # Wir suchen nach Mustern, die typisch für "Anfragen" sind
    social_noise = [
        r"\b(hallo|hi|hey|guten tag|servus)\b",
        r"\b(bitte|gerne|vielleicht|mal|einfach|gerade|eigentlich|halt)\b",
        r"\b(könntest du|würdest du|kannst du|ich möchte|ich brauche|hilf mir|zeige mir)\b",
        r"\b(vielen dank|danke im voraus|danke|viele grüße|beste grüße)\b",
        r"\b(ich würde mich freuen, wenn)\b"
    ]
    for pattern in social_noise:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)

    # --- EBENE 2: Erklärungs-Floskeln (Meta-Sprache) ---
    # Sätze, die nur beschreiben, DASS man etwas erklären soll
    meta_noise = [
        r"\b(erkläre mir|erläutere|beschreibe|ganz ausführlich|so einfach wie möglich)\b",
        r"\b(aufgrund der tatsache dass|es ist wichtig zu beachten dass|in der lage ist)\b",
        r"\b(programmiersprache|software|anwendung)\b"
    ]
    for pattern in meta_noise:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)

    # --- EBENE 3: Smarte Struktur-Korrektur ---
    # 1. Sprach-Erkennung (Extrahiert "auf Deutsch/Englisch" ans Ende)
    lang_match = re.search(r"\b(auf|in) (deutsch|englisch|german|english)\b", text, flags=re.IGNORECASE)
    if lang_match:
        lang = lang_match.group(2).capitalize()
        text = re.sub(r"\b(auf|in) (deutsch|englisch|german|english)\b", "", text, flags=re.IGNORECASE)
        text = text.strip() + f" [Sprache: {lang}]"

    # 2. Doppelte Sätze löschen (Deduplizierung)
    sentences = [s.strip() for s in text.split('.') if s.strip()]
    unique_sentences = []
    for s in sentences:
        if s.lower() not in [us.lower() for us in unique_sentences]:
            unique_sentences.append(s)
    text = ". ".join(unique_sentences)

    # --- EBENE 4: Clean-up (Kosmetik) ---
    text = text.replace(" und ", " & ").replace(" oder ", " | ")
    # Entfernt hängende Artikel/Präpositionen (z.B. "in der ", "für die ")
    text = re.sub(r"\b(in der|für die|eine|einen|dem|den|die|das|der)\b", "", text, flags=re.IGNORECASE)
    # Entfernt alle Satzzeichen am Anfang & doppelte Leerzeichen
    text = re.sub(r"^[!\?\.\s,]+", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    
    return text

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
