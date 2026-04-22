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

    # ==========================================
    # STEP 2: TRANSLATE THE MEMORY (DEFENSIVE PROGRAMMING)
    # ==========================================
    # Gradio frequently updates how they format 'history' (Lists vs Dictionaries vs Objects).
    # This loop checks the exact data type Gradio gave us and safely translates it
    # into the exact Dictionary format that the Groq API requires.
    for item in history:
        if isinstance(item, dict):
            # Gradio is using the New Dictionary format
            groq_history.append({"role": item["role"], "content": item["content"]})
        elif hasattr(item, 'role'):
            # Gradio is using the Newest Object format
            groq_history.append({"role": item.role, "content": item.content})
        else:
            # Gradio is using the Old List format [user_msg, ai_msg]
            groq_history.append({"role": "user", "content": item[0]})
            groq_history.append({"role": "assistant", "content": item[1]})

    # ==========================================
    # STEP 3: SEARCH THE VECTOR DATABASE (RAG)
    # ==========================================
    # We take the exact words the user just typed and mathematically search our ChromaDB
    # to see if we have any secret documents that relate to their question.
    results = collection.query(query_texts=[message], n_results=1)
    retrieved_text = results['documents'][0][0]



