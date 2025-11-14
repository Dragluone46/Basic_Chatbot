import streamlit as st
import requests
import json

OLLAMA_MODEL = "llama3:8b-instruct-q5_1"

with st.sidebar:
    st.image(r"C:\Users\ChristianDiCeglie\OneDrive - ITS Angelo Rizzoli\Immagini\Screenshot\Immagine 2025-04-09 143101.png")
    st.divider()
    st.caption("Developed by Dice")

    if st.button("🗑️ Cancella chat"):
            st.session_state.chat_history = []
            st.rerun()

st.title("Basic Chatbot Interface")

# Imposta modello di default (Ollama)
if "ollama_model" not in st.session_state:
    st.session_state["ollama_model"] = OLLAMA_MODEL

if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# ---- STREAMING con Ollama ----
def stream_ollama(prompt, model=OLLAMA_MODEL, timeout=300):
    """
    Generatore che restituisce chunk di testo dallo stream di Ollama.
    """
    url = "http://localhost:11434/api/generate"
    payload = {"model": model, 
               "prompt": prompt, 
               "stream": True}
    try:
        with requests.post(url, json=payload, stream=True, timeout=timeout) as r:
            r.raise_for_status()
            for line in r.iter_lines(decode_unicode=True):
                if not line:
                    continue
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if "response" in obj and obj["response"]:
                    yield obj["response"]
                if obj.get("done"):
                    break
    except requests.RequestException as e:
        yield f"\n\n❌ Errore di streaming da Ollama: {e}"

prompt = st.chat_input("Fammi una domanda...")

if prompt:
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    
    for message in st.session_state.chat_history:
        with st.chat_message(name=message["role"]):
            st.markdown(message["content"])

    ai_container = st.chat_message("ai")
    with ai_container:
        with st.spinner("Sto pensando..."):
            response = ""
            response_box = st.empty()
            for chunk in stream_ollama(prompt):
                response += chunk
                response_box.markdown(response)

    st.session_state.chat_history.append({"role": "ai", "content": response})