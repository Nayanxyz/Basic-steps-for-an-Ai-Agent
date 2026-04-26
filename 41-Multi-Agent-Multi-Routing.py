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
        {"role": "system", "content": """You are the Orchestrator. Read the user's input and route it.
You must output ONLY a comma-separated list of departments.
CRITICAL: DO NOT explain your reasoning. DO NOT output full sentences. ONLY output the department names.

ROUTING RULES:
1. Output 'WEB' for live events, weather, sports, recent news.
2. Output 'RAG' for internal company data, passwords, or documents.
3. Output 'CHAT' for small talk, hellos, or general AI conversation.
4. Output 'MATH' for calculation mathematics.

EXAMPLES:
User: "What is the weather and what is 2+2?" -> WEB, MATH
User: "What is the company wifi?" -> RAG
User: "Hello there!" -> CHAT"""},
        {"role": "user", "content": user_text}
    ]
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    payload = {"model": "llama-3.1-8b-instant", "messages": orchestrator_prompt, "temperature": 0.0}
    response = requests.post(CLOUD_URL, headers=headers, json=payload)
    return response.json()["choices"][0]["message"]["content"].strip().upper()

# The Micro Agent for WEb Scraping
def get_wiki_topic(user_text):
    topic_prompt = [
        {"role": "system", "content": """You are a search term extractor. Read the user's prompt and extract ONLY the main Wikipedia search topic.
Ignore math, ignore small talk, and ignore internal company questions. Output EXACTLY ONE phrase.
Example: 'What is 5+5 and who won the 2024 super bowl?' -> 'Super Bowl LVIII'
Example: 'Hello, who is the CEO of Apple?' -> 'CEO of Apple'"""},
        {"role": "user", "content": user_text}
    ]
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    payload = {"model": "llama-3.1-8b-instant", "messages": topic_prompt, "temperature": 0.0}
    response = requests.post(CLOUD_URL, headers=headers, json=payload)
    return response.json()["choices"][0]["message"]["content"].strip()

