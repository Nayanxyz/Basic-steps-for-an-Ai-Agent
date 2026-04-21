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


