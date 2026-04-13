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
    # Level 1 Regeln: Höflichkeit & Whitespace entfernen
    text = re.sub(r"(Hallo|Guten Tag|Bitte|Könntest du|Danke),?", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\s+", " ", text).strip()
    text = text.replace(" und ", " & ").replace(" oder ", " | ")
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
