import json as js

chat_history = []
print("type 'exit' to stop" )

while True:
    user_input = input("You: ")

    if user_input == "exit":
        network_payload = js.dumps(chat_history, indent=4)

        print("Sending payload to server...")
        print(network_payload)

        break

    dictionary = {"role": "user", "content": user_input}

    chat_history.append(dictionary)

    ai_response = "I am a simulated Ai"
    response = {"role": "assistant", "content": ai_response}
    chat_history.append(response)

    print(chat_history)