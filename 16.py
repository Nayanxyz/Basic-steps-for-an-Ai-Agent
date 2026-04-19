import requests

local_url = "http://localhost:11434/api/chat"


def send_to_local_ai(history_list):
    # 1. Build the Envelope (The Schema Ollama expects)
    payload_envelope = {
        "model": "llama3",  # Or whatever model you downloaded (e.g., "phi3")
        "messages": history_list,
        "stream": False  # We want the whole message at once
    }

    # 2. Fire the request. (Using json= handles the dumps() and headers for us)
    print("Agent: Thinking...")
    server_response = requests.post(local_url, json=payload_envelope)

    # 3. Unpack the response from a <Response [200]> object into a Python dictionary
    response_data = server_response.json()

    # 4. Drill into the dictionary to extract just the AI's words
    # (Remember the structure from the last lesson: data -> message -> content)
    ai_text = response_data["message"]["content"]

    return ai_text

# --- Quick Test ---
# test_history = [{"role": "user", "content": "What is 2+2? Answer in one word."}]
# print(send_to_local_ai(test_history))