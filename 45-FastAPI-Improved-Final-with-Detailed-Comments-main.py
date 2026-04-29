# === KEY STEP 1: TOOLBOX IMPORTS ===
from ddgs import DDGS                                                                                                # Imports DuckDuckGo search tool for live news
from fastapi import FastAPI                                                                                          # Imports FastAPI framework to build the web server
from pydantic import BaseModel                                                                                       # Imports Pydantic to validate incoming JSON data
import uvicorn                                                                                                       # Imports Uvicorn server to run the FastAPI app
import os                                                                                                            # Imports OS module to read environment variables
import requests                                                                                                      # Imports Requests to make API calls to Groq
import chromadb                                                                                                      # Imports ChromaDB for local vector database (RAG)
import re                                                                                                            # Imports Regular Expressions for text filtering
from dotenv import load_dotenv                                                                                       # Imports dotenv to load secret keys from a .env file
from datetime import datetime                                                                                        # Imports datetime to get the current date and time

# === KEY STEP 2: ENVIRONMENT SETUP ===
load_dotenv()                                                                                                        # Loads the hidden passwords from the local .env file
API_KEY = os.getenv("GROQ_API_KEY")                                                                                  # Safely grabs the Groq API key from memory
CLOUD_URL = "https://api.groq.com/openai/v1/chat/completions"                                                        # Sets the exact URL for the Groq supercomputer

# === KEY STEP 3: SERVER & DATABASE INITIALIZATION ===
app = FastAPI(title="Enterprise Swarm API", version="1.0")                                                           # Initializes the FastAPI server application
active_sessions = {}                                                                                                 # Creates an empty dictionary to hold chat histories for different users

client = chromadb.Client()                                                                                           # Boots up the local ChromaDB database client
collection = client.get_or_create_collection(name="chroma_collection")                                               # Creates or opens a digital folder for company data

try:                                                                                                                 # Starts a safe execution block
    collection.add(documents=["The company wifi password is 'BlueMonkey42'."], ids=["doc1"])                         # Injects the company password into the database
except:                                                                                                              # Catches the error if the password is already in the database
    pass                                                                                                             # Ignores the error and keeps the server running smoothly

# === KEY STEP 4: DATA CONTRACTS (PYDANTIC) ===
class UserRequest(BaseModel):                                                                                        # Defines the strict input rules for the API
    user_id: str                                                                                                     # Demands that the incoming request must have a string ID
    prompt: str                                                                                                      # Demands that the incoming request must have a text prompt

class SwarmResponse(BaseModel):                                                                                      # Defines the strict output rules for the API
    manager_routing: str                                                                                             # Promises the output will contain the routing decision
    final_answer: str                                                                                                # Promises the output will contain the final AI text


# === KEY STEP 5: CORE AI WORKERS ===
def get_manager_decision(user_text):                                                                                 # Defines the Orchestrator function

    orchestrator_prompt = [                                                                                          # Creates the message list for the AI
        {"role": "system", "content": """You are the Orchestrator. Route the user's input.
You must output ONLY a comma-separated list of departments. DO NOT explain your reasoning.
ROUTING RULES:
1. Output 'WEB' for live events, weather, sports, recent news.
2. Output 'RAG' for internal company data, passwords.
3. Output 'CHAT' for small talk.
4. Output 'MATH' for calculation mathematics."""},                                                                   # The strict rules for the Manager
        {"role": "user", "content": user_text}                                                                       # Injects the user's actual question
    ]

    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}                             # Packages the security badge
    payload = {"model": "llama-3.1-8b-instant", "messages": orchestrator_prompt, "temperature": 0.0}                 # Packages the API request with 0 creativity
    response = requests.post(CLOUD_URL, headers=headers, json=payload)                                               # Sends the request to Groq over the internet
    return response.json()["choices"][0]["message"]["content"].strip().upper()                                       # Extracts and cleans the one-word answer


