from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import os
import requests
import chromadb
import re
from dotenv import load_dotenv
from bs4 import BeautifulSoup

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


