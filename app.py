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
    # 1. Ganze Höflichkeits-Sätze entfernen (Aggressiv)
    fluff_phrases = [
        r"Ich würde mich sehr freuen, wenn du mir (.*) könntest",
        r"Ich bitte dich, mir das (.*) zu erklären",
        r"Es ist wichtig zu beachten, dass",
        r"Selbstverständlich verstehe ich, dass (.*)",
        r"Vielen Dank", 
        r"Danke im Voraus",
        r"in der Lage ist,",
        r"aufgrund der Tatsache, dass"
    ]
    for phrase in fluff_phrases:
        text = re.sub(phrase, "", text, flags=re.IGNORECASE)

    # 2. Doppelte Informationen/Sätze löschen (Simpel)
    # Wenn ein Satz exakt so nochmal vorkommt, löschen wir ihn
    sentences = text.split('.')
    unique_sentences = []
    for s in sentences:
        if s.strip() not in unique_sentences:
            unique_sentences.append(s.strip())
    text = ". ".join(unique_sentences)

    # 3. Sprach-Anweisungen bündeln
    if "Deutsch" in text:
        text = re.sub(r"(Antworte|Erklärung|Antwort) auf Deutsch(\.)?", "", text, flags=re.IGNORECASE)
        text += " Antwort-Sprache: Deutsch."

    # 4. Programmier-Kontext kürzen
    text = text.replace("Programmiersprache Python", "Python")

    # 5. Klassische Level 1 Regeln (Satzzeichen & Whitespace)
    text = re.sub(r"(Hallo|Bitte|Könntest du|Könnte),?", "", text, flags=re.IGNORECASE)
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
