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

