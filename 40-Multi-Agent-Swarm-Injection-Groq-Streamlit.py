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


