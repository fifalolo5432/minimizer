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
    # 1. Ganze Sätze löschen, die typischerweise "Lärm" sind
    # (Intro & Outro Block-Löschung)
    noise_sentences = [
        r"ich hoffe,? es geht dir (heute )?gut",
        r"ich würde mich (sehr )?freuen,? wenn",
        r"ich (bitte|suche|brauche) dich,?",
        r"für deine bemühungen",
        r"vielen dank im voraus",
        r"danke im voraus",
        r"im voraus &",
        r"es ist so, dass",
        r"ich möchte,? dass du mir"
    ]
    for pattern in noise_sentences:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)

    # 2. Aggressiver Wort-Filter (Wortgrenzen sind wichtig!)
    # Wir löschen Wörter, die fast nie Information tragen
    kill_list = [
        r"\b(bitte|vielleicht|eigentlich|gerade|mal|halt|eben|einfach|gerne)\b",
        r"\b(könntest|würdest|kannst|möchte|hätte|wäre)\b",
        r"\b(hallo|hi|hey|liebes ki-modell|liebe ki)\b",
        r"\b(antworte|antwort|erklärung|erkläre mir)\b"
    ]
    for pattern in kill_list:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)

    # 3. Sprach-Zusammenführung (Smart)
    if "deutsch" in text.lower():
        text = re.sub(r"\b(auf|in) deutsch\b", "", text, flags=re.IGNORECASE)
        text = text.strip() + " [Sprache: Deutsch]"

    # 4. Radikaler Struktur-Schnitt (Satzfragmente säubern)
    # Wir löschen Pronomen, die nach dem Löschen von Verben allein stehen
    text = re.sub(r"\b(ich|du|dir|mir|mein|meinem|meinen|dich|dein|deine|euer|ihr)\b", "", text, flags=re.IGNORECASE)
    
    # 5. Clean-up (Der "Hausmeister")
    text = text.replace(" und ", " & ").replace(" oder ", " | ")
    # Lösche alle Artikel und Präpositionen, die jetzt oft nutzlos rumstehen
    text = re.sub(r"\b(der|die|das|ein|eine|einen|dem|den|an|am|für|zu)\b", "", text, flags=re.IGNORECASE)
    
    # Entferne Satzzeichen-Müll und doppelte Leerzeichen
    text = re.sub(r"[!,\.;\?]+", " ", text) # Alle Satzzeichen durch Leerzeichen ersetzen
    text = re.sub(r"\s+", " ", text).strip() # Doppelte Leerzeichen killen
    
    # Ersten Buchstaben groß schreiben für die Optik
    return text[0].upper() + text[1:] if text else ""

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
