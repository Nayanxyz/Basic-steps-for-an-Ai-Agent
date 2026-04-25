import streamlit as st
import os
import requests
import json as js
import chromadb
import re
from dotenv import load_dotenv
from bs4 import BeautifulSoup

load_dotenv()

# ==========================================
# 1. THE BRAIN & TOOLS
# ==========================================
API_KEY = os.getenv("GROQ_API_KEY")
CLOUD_URL = "https://api.groq.com/openai/v1/chat/completions"


def fetch_weather(city):
    return f"It is 75 degrees and sunny in {city}."


def send_to_cloud_ai(history_list):
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    payload = {"model": "llama-3.1-8b-instant", "messages": history_list, "temperature": 0.7}
    response = requests.post(CLOUD_URL, headers=headers, json=payload)
    return response.json()["choices"][0]["message"]["content"]

def compress_memory(history_list):
    compression_payload = [
        {"role": "system",
         "content": "You are a memory compressor. Summarize the conversation into 3 concise bullet points. Retain critical facts like names, locations, and tasks."},
        {"role": "user", "content": f"Here is the raw conversation log: {str(history_list)}"}
    ]

    data = send_to_cloud_ai(compression_payload)
    return data

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

# ==========================================
# 2. THE CACHED DATABASE
# ==========================================
@st.cache_resource
def setup_database():
    client = chromadb.Client()
    collection = client.create_collection(name="chroma_collection")
    secret_doc = "The company wifi password is 'BlueMonkey42'."
    collection.add(documents=[secret_doc], ids=["doc1"])
    return collection


collection = setup_database()

# ==========================================
# 3. THE FRONTEND UI & MEMORY
# ==========================================
st.title("Enterprise RAG Agent")

# --- CHANGE 1: AGGRESSIVE SYSTEM PROMPT ---
# We explicitly forbid the AI from saying "I don't know" and demand the JSON tool.
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        {"role": "system", "content": """You are an advanced AI assistant. You have access to TWO tools:
1. get_weather: Fetches the current weather for a city.
   JSON Format: {"tool": "get_weather", "location": "City Name"}
2. scrape_wikipedia: Searches Wikipedia for facts, history, or news.
   JSON Format: {"tool": "scrape_wikipedia", "topic": "Search_Term_With_Underscores"}

STRICT RULE: If you need to use a tool, you MUST output ONLY the JSON object. 
NEVER apologize. NEVER mention your knowledge cutoff. If you don't know the answer, use the scrape_wikipedia tool immediately."""}
    ]

for message in st.session_state.chat_history:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.write(message["content"])

# ==========================================
# 4. THE RAG INJECTION LOOP
# ==========================================
if user_input := st.chat_input("Ask about the company or weather..."):

    # 1. THE VISIBLE COMMIT
    with st.chat_message("user"):
        st.write(user_input)
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    # ==========================================
    # --- NEW: THE BACKGROUND JANITOR ---
    # ==========================================
    # If our memory has more than 6 items (System prompt + 5 interactions)
    if len(st.session_state.chat_history) > 6:
        print("\n--- JANITOR TRIGGERED: Compressing Memory ---")

        # 1. Get the summary
        compressed_text = compress_memory(st.session_state.chat_history)

        # 2. Grab the Buns
        top_bun = st.session_state.chat_history[0]
        bottom_bun = st.session_state.chat_history[-1]

        # 3. Create the Meat
        summary_meat = {"role": "system", "content": f"Previous Conversation Summary:\n{compressed_text}"}

        # 4. The Live Splice (Overwrite the real memory!)
        st.session_state.chat_history = [top_bun, summary_meat, bottom_bun]
        print("--- COMPRESSION COMPLETE ---")
    # ==========================================

    # 2. Search Database
    results = collection.query(query_texts=[user_input], n_results=1)
    retrieved_text = results['documents'][0][0]

    # 3. THE SHADOW CLONE
    temp_memory = st.session_state.chat_history.copy()

    # --- CHANGE 2: AGGRESSIVE FINAL PROMPT ---
    # We softened the "ONLY use this context" rule and reminded it to use the tool.
    # --- FIX 1: Allow Wikipedia in the prompt ---
    final_prompt = f"Company Context: '{retrieved_text}'. INSTRUCTION: If the user asks about weather, news, sports, or facts, you MUST use your tools. Do not say 'I don't know'. Question: {user_input}"
    temp_memory[-1] = {"role": "user", "content": final_prompt}

    # 4. Send the CLONE to the Brain
    with st.spinner("Agent is thinking..."):
        ai_words = send_to_cloud_ai(temp_memory)

        # 5. THE REGEX INTERCEPTOR
        match = re.search(r'\{.*?\}', ai_words, re.DOTALL)

        if match:
            clean_json_string = match.group(0)
            tool_data = js.loads(clean_json_string)
            tool_name = tool_data.get("tool", "")

            if tool_name == "get_weather":
                city = tool_data.get("location", "an unknown city")
                weather_result = fetch_weather(city)

                # --- CHANGE 3: RULE OVERRIDE ---
                # We give the AI permission to stop acting like a robot and speak normally.
                temp_memory.append({"role": "assistant", "content": clean_json_string})
                temp_memory.append({"role": "user",
                                    "content": f"System Tool Output: {weather_result}. Read this data and answer the user directly. CRITICAL: Do NOT mention rules, overrides, tools, or JSON. Just answer the question naturally."})

                ai_words = send_to_cloud_ai(temp_memory)

            elif tool_name == "scrape_wikipedia":
                search = tool_data.get("topic", "Search_term")
                scrape = scrape_wikipedia(search)

                temp_memory.append({"role": "assistant", "content": clean_json_string})
                temp_memory.append({"role": "user",
                                    "content": f"System Tool Output: {scrape}. Read this data and answer the user directly. CRITICAL: Do NOT mention rules, overrides, tools, or JSON. Just answer the question naturally."})

                ai_words = send_to_cloud_ai(temp_memory)

    # 6. DRAW THE FINAL AI RESPONSE TO THE SCREEN
    with st.chat_message("assistant"):
        st.write(ai_words)

    # 7. Save final AI response to REAL memory
    st.session_state.chat_history.append({"role": "assistant", "content": ai_words})