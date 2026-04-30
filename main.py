from ddgs import DDGS
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
import os
import requests
import chromadb
import re
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY")
CLOUD_URL = "https://api.groq.com/openai/v1/chat/completions"

# ==========================================
# 1. API INITIALIZATION & MEMORY STORE
# ==========================================
app = FastAPI(title="Enterprise Swarm API", version="1.0")

# [API UPGRADE]: We replace st.session_state with a dictionary to hold multiple users.
active_sessions = {}

# Initialize ChromaDB once when the server boots up
client = chromadb.Client()
collection = client.get_or_create_collection(name="chroma_collection")
# Safe add: We use get_or_create so it doesn't crash if it already exists
try:
    collection.add(documents=["The company wifi password is 'BlueMonkey42'."], ids=["doc1"])
except:
    pass


# ==========================================
# 2. PYDANTIC DATA CONTRACTS
# ==========================================
class UserRequest(BaseModel):
    user_id: str
    prompt: str


class SwarmResponse(BaseModel):
    manager_routing: str
    final_answer: str


# ==========================================
# 3. CORE AI FUNCTIONS (Unchanged from Phase 10)
# ==========================================
def get_manager_decision(user_text):
    orchestrator_prompt = [
        {"role": "system", "content": """You are the Orchestrator. Route the user's input.
You must output ONLY a comma-separated list of departments. DO NOT explain your reasoning.
ROUTING RULES:
1. Output 'WEB' for live events, weather, sports, recent news.
2. Output 'RAG' for internal company data, passwords.
3. Output 'CHAT' for small talk.
4. Output 'MATH' for calculation mathematics."""},
        {"role": "user", "content": user_text}
    ]
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    payload = {"model": "llama-3.1-8b-instant", "messages": orchestrator_prompt, "temperature": 0.0}
    response = requests.post(CLOUD_URL, headers=headers, json=payload)
    return response.json()["choices"][0]["message"]["content"].strip().upper()

# The Micro Agent
def get_search_query(user_text):
    today = datetime.now().strftime("%B %d, %Y")
    current_year = datetime.now().year

    topic_prompt = [
        {"role": "system", "content": f"""You are an SEO Search Expert. Today is {today}.
Your ONLY job is to extract the live news or web search topic from the user's prompt.
CRITICAL RULES:
1. IGNORE math equations.
2. IGNORE internal company questions (passwords, wifi, etc.).
3. If the user asks about current events, append the year '{current_year}' to the search string.
4. Output EXACTLY ONE string. Do not talk.

EXAMPLES:
User: "What is 5+5 and who won the Super Bowl?" -> "Super Bowl winner {current_year}"
User: "what is wifi password, Bengal election results, and 8/2?" -> "Bengal election results {current_year}"
User: "Hello, what is the weather in Tokyo?" -> "Tokyo weather {today}"
"""},
        {"role": "user", "content": user_text}
    ]

    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    payload = {"model": "llama-3.1-8b-instant", "messages": topic_prompt, "temperature": 0.0}
    response = requests.post(CLOUD_URL, headers=headers, json=payload)
    return response.json()["choices"][0]["message"]["content"].strip()


def send_to_cloud_ai(history_list):
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    payload = {"model": "llama-3.1-8b-instant", "messages": history_list, "temperature": 0.7}
    response = requests.post(CLOUD_URL, headers=headers, json=payload)
    return response.json()["choices"][0]["message"]["content"]


def compress_memory(history_list):
    compression_payload = [
        {"role": "system",
         "content": "You are a backend memory manager. Generate a detailed 'Running Fact Sheet' from the log."},
        {"role": "user", "content": str(history_list)}
    ]
    return send_to_cloud_ai(compression_payload)


def calculate_math(expression):
    return eval(str(expression))

