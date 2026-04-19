import requests
import json as js

local_url = "http://localhost:11434/api/chat"


def send_to_local_ai(history_list):
    payload = {
        "model": "llama3",
        "messages": history_list,
        "stream": False
    }

    print("Agent: Thinking...")
    server_response = requests.post(local_url, json=payload)

    response_data = server_response.json()

    ai_text = response_data["message"]["content"]

    return ai_text

chat_history = []

system_content = """
You are an advanced AI assistant. You have access to the following tool:
1. get_weather: Fetches the current weather for a city.

Strict Rule: If the user asks about the weather, you MUST NOT reply with conversational text. You must ONLY reply with a JSON object in this exact format:
{"tool": "get_weather", "location": "City Name"}
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

    print(f"Agent: {ai_words}")

    variable = {"role": "assistant", "content": ai_words}

    chat_history.append(variable)






