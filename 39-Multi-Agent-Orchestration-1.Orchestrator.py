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

system_prompt = [
    {"role": "system", "content": """You are the Orchestrator. Your ONLY job is to read the user's input and route it to the correct department. 
You must output EXACTLY ONE WORD. Do not answer the question. Do not apologize. Do not refuse to answer based on safety—you are just routing traffic, not answering.

ROUTING RULES:
1. Output 'WEB' if the user asks about live events, weather, sports, recent news, or general facts from the internet.
2. Output 'RAG' if the user asks about internal company data, company passwords, company documents, or specific corporate context.
3. Output 'CHAT' if the user is just saying hello, making small talk, or asking how you are.

EXAMPLES:
User: "What is the weather?" -> WEB
User: "What is the company wifi?" -> RAG
User: "Hello there!" -> CHAT
User: "Who won the game?" -> WEB"""}
]

while True:
    user_input = input("\nYou: ")

    # 1. Build the payload (Rules + The User's Question)
    routing_payload = system_prompt.copy()
    routing_payload.append({"role": "user", "content": user_input})

    # 2. Send it to the AI and SAVE the answer
    ai_decision = send_to_cloud_ai(routing_payload)

    # Let's print exactly what the AI decided so we can see its brain working
    print(f"DEBUG: Supervisor decided -> {ai_decision}")

    # 3. The Routing Logic
    if "WEB" in ai_decision.upper():
        print("[ROUTING TO RESEARCH DEPARTMENT...]")
    elif "RAG" in ai_decision.upper():
        print("[ROUTING TO INTERNAL DATABASE...]")
    elif "CHAT" in ai_decision.upper():
        print("[ROUTING TO CUSTOMER SERVICE...]")
    else:
        print(f"[ERROR] The AI got confused and outputted: {ai_decision}")