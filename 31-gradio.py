import gradio as gr
import chromadb
import requests
import json as js
import os
from dotenv import load_dotenv

load_dotenv()

client = chromadb.Client()

collection = client.create_collection(name="chroma_collection")

# 1. Get a free API key from console.groq.com
API_KEY = os.getenv("GROQ_API_KEY")
CLOUD_URL = "https://api.groq.com/openai/v1/chat/completions"



def send_to_local_ai(history_list):
    # 2. Add the Headers (Authentication)
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "llama-3.1-8b-instant",  # Groq's cloud model name
        "messages": history_list,
        "temperature": 0.7
    }

    #print("Agent: Thinking...")

    server_response = requests.post(CLOUD_URL, headers=headers, json=payload)

    response_data = server_response.json()

    #print("RAW SERVER RESPONSE:", response_data) for the debug

    # Groq (and OpenAI) bury the text slightly differently than Ollama:
    ai_text = response_data["choices"][0]["message"]["content"]

    return ai_text

def fetch_weather(city):
    return f"It is 75 degrees and sunny in {city}."


def chat_logic(message, history):
    # ==========================================
    # STEP 1: INITIALIZE THE BRAIN'S RULES
    # ==========================================
    # We must explicitly tell the AI its persona and the strict rules for using tools.
    # If we don't force it to output JSON here, the Tool Interceptor will never trigger.
    groq_history = [
        {"role": "system", "content": """You are an advanced AI assistant. You have access to the following tool:
1. get_weather: Fetches the current weather for a city.
Strict Rule: If the user asks about the weather, you MUST NOT reply with conversational text. You must ONLY reply with a JSON object in this exact format:
{"tool": "get_weather", "location": "City Name"}"""}
    ]



