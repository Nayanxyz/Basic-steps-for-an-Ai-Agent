from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import os
import requests
import chromadb
import re
from dotenv import load_dotenv
from bs4 import BeautifulSoup

load_dotenv()
API_KEY = os.getenv("GROQ_API_KEY")
CLOUD_URL = "https://api.groq.com/openai/v1/chat/completions"

# ==========================================
# 1. API INITIALIZATION & MEMORY STORE
# ==========================================
app = FastAPI(title="Enterprise Swarm API", version="1.0")

# [API UPGRADE]: We replace st.session_state with a dictionary to hold multiple users.
active_sessions = {}

# Initialize ChromaDB once when the server boots up
client = chromadb.Client()
collection = client.get_or_create_collection(name="chroma_collection")
# Safe add: We use get_or_create so it doesn't crash if it already exists
try:
    collection.add(documents=["The company wifi password is 'BlueMonkey42'."], ids=["doc1"])
except:
    pass


# ==========================================
# 2. PYDANTIC DATA CONTRACTS
# ==========================================
class UserRequest(BaseModel):
    user_id: str
    prompt: str


class SwarmResponse(BaseModel):
    manager_routing: str
    final_answer: str


# ==========================================
# 3. CORE AI FUNCTIONS (Unchanged from Phase 10)
# ==========================================
def get_manager_decision(user_text):
    orchestrator_prompt = [
        {"role": "system", "content": """You are the Orchestrator. Route the user's input.
You must output ONLY a comma-separated list of departments. DO NOT explain your reasoning.
ROUTING RULES:
1. Output 'WEB' for live events, weather, sports, recent news.
2. Output 'RAG' for internal company data, passwords.
3. Output 'CHAT' for small talk.
4. Output 'MATH' for calculation mathematics."""},
        {"role": "user", "content": user_text}
    ]
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    payload = {"model": "llama-3.1-8b-instant", "messages": orchestrator_prompt, "temperature": 0.0}
    response = requests.post(CLOUD_URL, headers=headers, json=payload)
    return response.json()["choices"][0]["message"]["content"].strip().upper()


def get_wiki_topic(user_text):
    topic_prompt = [
        {"role": "system", "content": """You are a strict data extractor. Extract the main Wikipedia search topic from the user's prompt. 
Output EXACTLY ONE NOUN PHRASE. DO NOT talk to the user. DO NOT echo instructions. If no clear Wikipedia topic exists, output 'NONE'."""},
        {"role": "user", "content": user_text}
    ]
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    payload = {"model": "llama-3.1-8b-instant", "messages": topic_prompt, "temperature": 0.0}
    response = requests.post(CLOUD_URL, headers=headers, json=payload)
    return response.json()["choices"][0]["message"]["content"].strip()


def send_to_cloud_ai(history_list):
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    payload = {"model": "llama-3.1-8b-instant", "messages": history_list, "temperature": 0.7}
    response = requests.post(CLOUD_URL, headers=headers, json=payload)
    return response.json()["choices"][0]["message"]["content"]


def compress_memory(history_list):
    compression_payload = [
        {"role": "system",
         "content": "You are a backend memory manager. Generate a detailed 'Running Fact Sheet' from the log."},
        {"role": "user", "content": str(history_list)}
    ]
    return send_to_cloud_ai(compression_payload)


def calculate_math(expression):
    return eval(str(expression))


def scrape_wikipedia(topic):
    clean_topic = topic.replace(" ", "_")
    print(f"\n[SERVER LOG] Scraping Wikipedia for: '{clean_topic}'")
    url = f"https://en.wikipedia.org/wiki/{clean_topic}"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    massive_string = ""
    for paragraph in soup.find_all('p'):
        massive_string += paragraph.get_text() + "\n"
    return massive_string[:2000]


# ==========================================
# 4. THE API ENDPOINT (The Swarm Pipeline)
# ==========================================
@app.post("/chat", response_model=SwarmResponse)
async def chat_with_swarm(request: UserRequest):
    print(f"\n--- NEW REQUEST FROM [{request.user_id}] ---")

    # [API UPGRADE]: Pull up the specific user's memory, or create a new one if they are new
    if request.user_id not in active_sessions:
        active_sessions[request.user_id] = [
            {"role": "system",
             "content": "You are the Senior Synthesis AI. Answer clearly using the provided system data."}
        ]

    # 1. Commit user message to their specific memory
    user_history = active_sessions[request.user_id]
    user_history.append({"role": "user", "content": request.prompt})

    # 2. Background Janitor
    if len(user_history) > 6:
        print(f"[SERVER LOG] Compressing memory for {request.user_id}...")
        compressed_text = compress_memory(user_history[:-1])
        active_sessions[request.user_id] = [user_history[0],
                                            {"role": "system", "content": f"Fact Sheet:\n{compressed_text}"},
                                            user_history[-1]]
        user_history = active_sessions[request.user_id]

    # 3. Manager Routing
    decision = get_manager_decision(request.prompt)
    print(f"[SERVER LOG] Manager routed to: {decision}")

    # 4. The Pipeline
    temp_memory = user_history.copy()
    collected_context = ""

    if "RAG" in decision:
        results = collection.query(query_texts=[request.prompt], n_results=1)
        # Wrap data in clear XML tags
        collected_context += f"<internal_company_data>\n{results['documents'][0][0]}\n</internal_company_data>\n\n"

    if "WEB" in decision:
        wiki_topic = get_wiki_topic(request.prompt)
        if wiki_topic != "NONE":
            scrape_data = scrape_wikipedia(wiki_topic)
            collected_context += f"<wikipedia_data topic='{wiki_topic}'>\n{scrape_data}\n</wikipedia_data>\n\n"

    if "MATH" in decision:
        math_expression = re.sub(r'[^0-9\+\-\*\/\(\)\.]', '', request.prompt)
        try:
            collected_context += f"<math_calculation>\n{calculate_math(math_expression)}\n</math_calculation>\n\n"
        except:
            pass

    # 5. Final Synthesis
    if collected_context != "":
        # Give the AI crystal clear instructions on how to read the XML
        final_prompt = f"""You are a helpful Enterprise AI. Read the XML data provided below. 
    You must address EVERY question the user asked. Do not leave anything out. Do not mention the XML tags to the user.

    SYSTEM DATA:
    {collected_context}

    USER PROMPT: {request.prompt}"""
        temp_memory[-1] = {"role": "user", "content": final_prompt}

    ai_words = send_to_cloud_ai(temp_memory)

    # 6. Final Commit & Return Payload
    user_history.append({"role": "assistant", "content": ai_words})

    print("--- REQUEST COMPLETE ---")

    return SwarmResponse(
        manager_routing=decision,
        final_answer=ai_words
    )


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)