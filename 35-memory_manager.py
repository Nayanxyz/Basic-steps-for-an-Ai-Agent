import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")
CLOUD_URL = "https://api.groq.com/openai/v1/chat/completions"

def send_to_cloud_ai(history_list):
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    payload = {"model": "llama-3.1-8b-instant", "messages": history_list, "temperature": 0.7}
    response = requests.post(CLOUD_URL, headers=headers, json=payload)
    return response.json()["choices"][0]["message"]["content"]

long_history = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": "Hi, my name is Alex and I live in New York."},
    {"role": "assistant", "content": "Nice to meet you, Alex from New York! How can I help?"},
    {"role": "user", "content": "I am a software engineer building an AI startup."},
    {"role": "assistant", "content": "That sounds exciting! What kind of AI?"},
    {"role": "user", "content": "A web-scraping RAG agent for financial data."},
    {"role": "assistant", "content": "Very cool. Do you need help with the architecture?"},
    {"role": "user", "content": "Yes, but first, what did I say my name was?"}
]

def compress_memory(history_list):
    compression_payload = [
        {"role": "system",
         "content": "You are a memory compressor. Summarize the conversation into 3 concise bullet points. Retain critical facts like names, locations, and tasks."},
        {"role": "user", "content": f"Here is the raw conversation log: {str(history_list)}"}
    ]

    data = send_to_cloud_ai(compression_payload)
    return data



