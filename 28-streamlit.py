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


