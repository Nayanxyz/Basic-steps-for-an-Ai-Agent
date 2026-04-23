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


    results = collection.query(query_texts=[message], n_results=1)
    retrieved_text = results['documents'][0][0]


    final_prompt = f"Company Context: '{retrieved_text}'. INSTRUCTION: If the user asks about sports, news, or 2024, you MUST use the scrape_wikipedia tool. Do not say 'I don't know'. Question: {message}"
    groq_history.append({"role": "user", "content": final_prompt})

    # We send the entire conversation history to the cloud to get the AI's first thought.
    ai_words = send_to_local_ai(groq_history)

    # ==========================================
    # STEP 5: THE TOOL INTERCEPTOR (REGEX NET)
    # ==========================================
    # We check if the AI's response contains '{}' brackets and the word 'tool'.
    # If it does, we assume it is trying to run a Python function, NOT talk to the user.
    if "{" in ai_words and "}" in ai_words and "tool" in ai_words.lower():
        try:
            import re
            # REGEX MAGIC: Llama 3 often wraps JSON in markdown (```json ... ```).
            # This regex rips away everything except the pure dictionary inside { }.
            match = re.search(r'\{.*?\}', ai_words, re.DOTALL)

            if match:
                clean_json_string = match.group(0)
                tool_data = js.loads(clean_json_string)
                tool_name = tool_data.get("tool", "")

                if tool_name == "get_weather":
                    # Extract the city, or default to 'an unknown city' if the AI forgot to include it.
                    city = tool_data.get("location", "an unknown city")

                    # Actually run our Python function to get the real-world data
                    weather_result = fetch_weather(city)

                    groq_history.append({"role": "user",
                                         "content": f"System Tool Output: {weather_result}."
                                                    f" RULE OVERRIDE: You have the data. Do NOT output JSON. Answer the user naturally in plain, friendly text."})

                    ai_final_words = send_to_local_ai(groq_history)
                    return ai_final_words  # Send the final English sentence to the Gradio UI

                elif tool_name == "scrape_wikipedia":
                    search = tool_data.get("topic","Search_term" )
                    scrape = scrape_wikipedia(search)

                    groq_history.append({"role": "user", "content": f"System Tool Output: {scrape}."
                                                                    f" RULE OVERRIDE: You have the data. Do NOT output JSON. Answer the user naturally in a plain, friendly paragraph."})

                    ai_final_words = send_to_local_ai(groq_history)
                    return ai_final_words

                else:
                    return f"System Error: Unknown tool requested -> {tool_name}"

            else:
                return ai_words  # Failsafe: If regex fails to find brackets, just print what it said

        except Exception as e:
            # If the JSON was completely broken, we print an error so the developer can see it.
            return f"System Error: The AI formatted the tool request incorrectly. Raw output: {ai_words}"

    else:

        return ai_words


secret_doc = "The company wifi password is 'BlueMonkey42'."
collection.add(documents=[secret_doc], ids=["doc1"])

app = gr.ChatInterface(fn=chat_logic)
app.launch(share=True)
