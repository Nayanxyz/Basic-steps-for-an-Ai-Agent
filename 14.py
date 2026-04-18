chat_history = []
print("type 'exit' to stop" )

while True:
    user_input = input("You: ")

    if user_input == "exit":
        print("Thank you!")
        break

    dictionary = {"role": "user", "content": user_input}

    chat_history.append(dictionary)

