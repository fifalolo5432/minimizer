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
    # A. Die "Müll-Liste" (Linguistische Kleinst-Teile)
    # Diese Wörter können fast immer weg, ohne den Sinn zu rauben
    fillers = [
        r"\bbitte\b", r"\bkönntest du\b", r"\bwäre es möglich\b", 
        r"\beigentlich\b", r"\bvielleicht\b", r"\bmal\b", r"\beinfach\b",
        r"\bhallo\b", r"\bguten tag\b", r"\bdanke\b", r"\bvielen dank\b"
    ]
    for pattern in fillers:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)

    # B. Verben-Kürzung (Aktivierung)
    # Macht aus "Ich möchte, dass du mir erklärst" -> "Erkläre"
    text = re.sub(r"ich möchte,? dass du mir (.*) erklärst", r"Erkläre \1", text, flags=re.IGNORECASE)
    text = re.sub(r"kannst du mir (.*) zeigen", r"Zeige \1", text, flags=re.IGNORECASE)

    # C. Smarte Sprach-Erkennung
    # Sucht nach "auf Deutsch", "in Deutsch", "auf Englisch" etc.
    lang_match = re.search(r"(auf|in) (Deutsch|Englisch|Französisch|Spanisch)", text, flags=re.IGNORECASE)
    if lang_match:
        lang = lang_match.group(2)
        text = re.sub(r"(auf|in) (Deutsch|Englisch|Französisch|Spanisch)", "", text, flags=re.IGNORECASE)
        text = text.strip() + f" [Sprache: {lang}]"

    # D. Technisches Markup (Struktur statt Prosa)
    text = text.replace("Programmiersprache ", "")
    
    # E. Whitespace & Satzzeichen-Reinigung
    text = re.sub(r"\s+", " ", text) # Doppelte Leerzeichen
    text = re.sub(r"\.+", ".", text) # Doppelte Punkte
    
    return text.strip()

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
