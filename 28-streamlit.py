import streamlit as st
import os
import requests
import json as js
import chromadb
from dotenv import load_dotenv

load_dotenv()

# ==========================================
# 1. THE BRAIN (Groq Setup)
# ==========================================
API_KEY = os.getenv("GROQ_API_KEY")
CLOUD_URL = "https://api.groq.com/openai/v1/chat/completions"


def send_to_cloud_ai(history_list):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama-3.1-8b-instant",
        "messages": history_list,
        "temperature": 0.7
    }
    response = requests.post(CLOUD_URL, headers=headers, json=payload)
    return response.json()["choices"][0]["message"]["content"]


# ==========================================
# 2. THE CACHED DATABASE (Runs only ONCE)
# ==========================================
@st.cache_resource
def setup_database():
    client = chromadb.Client()
    collection = client.create_collection(name="chroma_collection")
    secret_doc = "The company wifi password is 'BlueMonkey42'."
    collection.add(documents=[secret_doc], ids=["doc1"])
    return collection


collection = setup_database()

# ==========================================
# 3. THE FRONTEND UI & MEMORY
# ==========================================
st.title("Enterprise RAG Agent")

# Initialize Chat History
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "system", "content": "You are a helpful AI assistant."}
    ]

# Draw existing messages (skipping the invisible system prompt)
for message in st.session_state.chat_history:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.write(message["content"])

# ==========================================
# 4. THE RAG INJECTION LOOP
# ==========================================
if user_input := st.chat_input("Ask about the company..."):
    # A. Show User Message
    with st.chat_message("user"):
        st.write(user_input)

    # B. Search Database
    results = collection.query(query_texts=[user_input], n_results=1)
    retrieved_text = results['documents'][0][0]

    # C. Build RAG Prompt (But we hide this ugly text from the UI)
    final_prompt = f"Answer using ONLY this context: {retrieved_text}. Question: {user_input}"

    # D. Save to memory and send to AI
    st.session_state.chat_history.append({"role": "user", "content": final_prompt})

    with st.spinner("Agent is searching documents..."):
        ai_response = send_to_cloud_ai(st.session_state.chat_history)

    # E. Show AI Response
    with st.chat_message("assistant"):
        st.write(ai_response)

    # F. Save AI response to memory
    st.session_state.chat_history.append({"role": "assistant", "content": ai_response})