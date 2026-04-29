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

