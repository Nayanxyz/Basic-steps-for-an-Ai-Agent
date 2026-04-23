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


    server_response = requests.post(CLOUD_URL, headers=headers, json=payload)

    response_data = server_response.json()

    #print("RAW SERVER RESPONSE:", response_data) for the debug

    # Groq (and OpenAI) bury the text slightly differently than Ollama:
    ai_text = response_data["choices"][0]["message"]["content"]

    return ai_text

def fetch_weather(city):
    return f"It is 75 degrees and sunny in {city}."


def scrape_wikipedia(topic):
    # 1. SANITIZE THE DATA: Replace all spaces with underscores
    clean_topic = topic.replace(" ", "_")

    # 2. DEBUGGER: Print it to the terminal so we can watch it work
    print(f"\n--- SCRAPER TRIGGERED: Searching for '{clean_topic}' ---\n")

    url = f"https://en.wikipedia.org/wiki/{clean_topic}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    # 2. Pass the headers into the get request
    response = requests.get(url, headers=headers)

    article = response.text

    soup = BeautifulSoup(article, 'html.parser')

    content = soup.find_all('p')

    massive_string = ""
    for paragraph in content:
        massive_string += paragraph.get_text() + "\n"

    return massive_string[:2000]


def chat_logic(message, history):
    groq_history = [
        {"role": "system", "content": """You are an advanced AI assistant. You have access to TWO tools:
1. get_weather: Fetches the current weather for a city.
   JSON Format: {"tool": "get_weather", "location": "City Name"}
2. scrape_wikipedia: Searches Wikipedia for facts, history, or news.
   JSON Format: {"tool": "scrape_wikipedia", "topic": "Search_Term_With_Underscores"}

STRICT RULE: If you need to use a tool, you MUST output ONLY the JSON object. 
NEVER apologize. NEVER mention your knowledge cutoff. If you don't know the answer, use the scrape_wikipedia tool immediately."""}

     ]

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



