# TOOL CALLING

import requests
import json as js
import os
from dotenv import load_dotenv

load_dotenv()
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

chat_history = []

system_content = """
You are an advanced AI assistant. You have access to the following tool:
1. get_weather: Fetches the current weather for a city.

Strict Rule: If the user asks about the weather, you MUST NOT reply with conversational text. You must ONLY reply with a JSON object in this exact format
"""
system_message = {"role": "system", "content": system_content}
chat_history.append(system_message)

print("Type 'exit' to shut down..")
while True:

    user_input = input("You: ")
    if user_input == "exit":
        print("Good bye!")
        break

    data = {"role": "user", "content": user_input}
    chat_history.append(data)

    ai_words = send_to_local_ai(chat_history)


    if "get_weather" in ai_words:
        tool_data = js.loads(ai_words)

        weather_result = fetch_weather(tool_data["location"])

        result_dict = {"role": "system", "content": weather_result}
        chat_history.append(result_dict)

        ai_final_words = send_to_local_ai(chat_history)
        print(f"Agent: {ai_final_words}")

        final_answer = ai_final_words

    else:
        print(f"Agent: {ai_words}")

        final_answer = ai_words

    variable = {"role": "assistant", "content": final_answer}

    chat_history.append(variable)