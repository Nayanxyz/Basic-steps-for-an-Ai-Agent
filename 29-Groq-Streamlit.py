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


def send_to_cloud_ai(history_list):
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    payload = {"model": "llama-3.1-8b-instant", "messages": history_list, "temperature": 0.7}
    response = requests.post(CLOUD_URL, headers=headers, json=payload)
    return response.json()["choices"][0]["message"]["content"]

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
st.title("Enterprise RAG Agent")

# --- CHANGE 1: AGGRESSIVE SYSTEM PROMPT ---
# We explicitly forbid the AI from saying "I don't know" and demand the JSON tool.
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "system", "content": """You are an advanced AI assistant. You have access to TWO tools:
1. get_weather: Fetches the current weather for a city.
   JSON Format: {"tool": "get_weather", "location": "City Name"}
2. scrape_wikipedia: Searches Wikipedia for facts, history, or news.
   JSON Format: {"tool": "scrape_wikipedia", "topic": "Search_Term_With_Underscores"}

STRICT RULE: If you need to use a tool, you MUST output ONLY the JSON object. 
NEVER apologize. NEVER mention your knowledge cutoff. If you don't know the answer, use the scrape_wikipedia tool immediately."""}
    ]

for message in st.session_state.chat_history:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.write(message["content"])

