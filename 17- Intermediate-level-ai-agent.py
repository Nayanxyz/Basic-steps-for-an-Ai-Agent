import requests
import json

local_url = "http://localhost:11434/api/chat"


def send_to_local_ai(history_list):
    # 1. Build the Envelope (The Schema Ollama expects)
    payload_envelope = {
        "model": "llama3",  # Ensure you have this model pulled in Ollama
        "messages": history_list,
        "stream": False  # We want the whole message at once
    }

    # 2. Fire the request
    print("Agent: Thinking...")
    server_response = requests.post(local_url, json=payload_envelope)

    # 3. Unpack the response and extract the text
    response_data = server_response.json()
    ai_text = response_data["message"]["content"]

    return ai_text


# --- THE MASTER LOOP (Memory Engine) ---

chat_history = []
print("Agent Memory Engine Online. Type 'exit' to stop.")

while True:
    user_input = input("\nYou: ")

    if user_input.lower() == "exit":
        print("Shutting down...")
        break

    # 1. Format and append the User's state
    user_dict = {"role": "user", "content": user_input}
    chat_history.append(user_dict)

    # 2. The Integration: Pass the memory to the AI and get the words back
    ai_words = send_to_local_ai(chat_history)

    # 3. Print the answer for the user
    print(f"Agent: {ai_words}")

    # 4. Format and append the AI's state so it remembers for the next loop
    ai_dict = {"role": "assistant", "content": ai_words}
    chat_history.append(ai_dict)