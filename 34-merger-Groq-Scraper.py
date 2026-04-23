import gradio as gr
import chromadb
import requests
import json as js
import os
from dotenv import load_dotenv
from bs4 import BeautifulSoup

load_dotenv()

client = chromadb.Client()

collection = client.create_collection(name="chroma_collection")

# 1. Get a free API key from console.groq.com
API_KEY = os.getenv("GROQ_API_KEY")
CLOUD_URL = "https://api.groq.com/openai/v1/chat/completions"



