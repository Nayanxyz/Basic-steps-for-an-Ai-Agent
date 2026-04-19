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
