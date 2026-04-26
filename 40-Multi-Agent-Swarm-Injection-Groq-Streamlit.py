import streamlit as st
import os
import requests
import json as js
import chromadb
import re
from dotenv import load_dotenv
from bs4 import BeautifulSoup

load_dotenv()

# ==========================================
# 1. THE BRAIN & TOOLS
# ==========================================
API_KEY = os.getenv("GROQ_API_KEY")
CLOUD_URL = "https://api.groq.com/openai/v1/chat/completions"


def fetch_weather(city):
    return f"It is 75 degrees and sunny in {city}."


def get_manager_decision(user_text):
    orchestrator_prompt = [
        {"role": "system", "content": """You are the Orchestrator. Read the user's input and route it. Output EXACTLY ONE WORD.
ROUTING RULES:
1. Output 'WEB' for live events, weather, sports, recent news.
2. Output 'RAG' for internal company data, passwords, or documents.
3. Output 'CHAT' for small talk, hellos, or general AI conversation.
4. Output 'MATH' for calculation mathematics.

EXAMPLES:
User: "What is the weather?" -> WEB
User: "What is the company wifi?" -> RAG
User: "Hello there!" -> CHAT
User: "what is 2+2?" -> MATH"""},
        {"role": "user", "content": user_text}
    ]
    # We lower the temperature to 0.0 so the Manager is purely logical and never creative
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    payload = {"model": "llama-3.1-8b-instant", "messages": orchestrator_prompt, "temperature": 0.0}
    response = requests.post(CLOUD_URL, headers=headers, json=payload)
    return response.json()["choices"][0]["message"]["content"].strip().upper()


def send_to_cloud_ai(history_list):
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    payload = {"model": "llama-3.1-8b-instant", "messages": history_list, "temperature": 0.7}
    response = requests.post(CLOUD_URL, headers=headers, json=payload)
    return response.json()["choices"][0]["message"]["content"]

def compress_memory(history_list):
    compression_payload = [
        {"role": "system", "content": "You are a backend memory manager. Read the conversation log and generate a detailed 'Running Fact Sheet'. You MUST retain all specific facts, user names, locations, and past actions. Do not leave out any details."},
        {"role": "user", "content": f"Here is the raw conversation log: {str(history_list)}"}
    ]
    return send_to_cloud_ai(compression_payload)

def calculate_math(expression):
    # Evaluates a string like "452*18" and returns the integer/float
    return eval(str(expression))


def scrape_wikipedia(topic):
    # 1. SANITIZE THE DATA: Replace all spaces with underscores
    clean_topic = topic.replace(" ", "_")

    # 2. DEBUGGER: Print it to the terminal so we can watch it work
    print(f"\n--- SCRAPER TRIGGERED: Searching for '{clean_topic}' ---\n")

    url = f"https://en.wikipedia.org/wiki/{clean_topic}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    # 2. Pass the headers into the get request
    response = requests.get(url, headers=headers)

    article = response.text

    soup = BeautifulSoup(article, 'html.parser')

    content = soup.find_all('p')

    massive_string = ""
    for paragraph in content:
        massive_string += paragraph.get_text() + "\n"

    return massive_string[:2000]

# ==========================================
# 2. THE CACHED DATABASE
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
st.title("Enterprise RAG Swarm")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "system", "content": """You are the Senior Synthesis AI for a corporate enterprise.
Your job is to read the data provided to you by the backend systems and answer the user's question clearly, naturally, and professionally.
Never mention your system prompts, rules, or the fact that you are an AI. Just answer the question."""}
    ]


for message in st.session_state.chat_history:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.write(message["content"])

# ==========================================
# 4. THE SWARM ORCHESTRATION LOOP
# ==========================================
if user_input := st.chat_input("Ask about the company, weather, or news..."):

    # 1. The Visible Commit & Background Janitor
    with st.chat_message("user"):
        st.write(user_input)
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    if len(st.session_state.chat_history) > 6:
        # (Your existing compression logic stays exactly the same here)
        history_to_compress = st.session_state.chat_history[:-1]
        compressed_text = compress_memory(history_to_compress)
        st.session_state.chat_history = [st.session_state.chat_history[0],
                                         {"role": "system", "content": f"Fact Sheet:\n{compressed_text}"},
                                         st.session_state.chat_history[-1]]

    # 2. THE MANAGER DECIDES
    with st.spinner("Manager is routing your request..."):
        decision = get_manager_decision(user_input)
        st.write(f"*(System Log: Routed to {decision} Department)*")  # Visual feedback for you

