def add_numbers(a, b):
    return a + b

def multiply_numbers(a, b):
    return a * b

def execute_agent(action_list):
    if action_list[0] == "add":
        return add_numbers(action_list[1], action_list[2])
    elif action_list[0] == "multiply":
        return multiply_numbers(action_list[1], action_list[2])

def parse_ai_output(text):
    chopped_list = text.replace("ACTION: ", "").split(" | ")
    command = chopped_list[0]
    num1 = int(chopped_list[1])
    num2 = int(chopped_list[2])
    return [command, num1, num2]

# --- THE MASTER LOOP ---
print("Agent is online. Type 'exit' to shut down.")

while True:
    user_input = input("You: ")

    if user_input == "exit":
        print("Shutting down agent...")
        break

    # DYNAMIC ADDITION
    elif user_input.startswith("add "):
        pieces = user_input.split(" ")
        fake_ai_thought = f"ACTION: add | {pieces[1]} | {pieces[2]}"

    # DYNAMIC MULTIPLICATION
    elif user_input.startswith("multiply "):
        pieces = user_input.split(" ")
        fake_ai_thought = f"ACTION: multiply | {pieces[1]} | {pieces[2]}"

    else:
        print("Agent: I don't know how to do that yet.")
        continue

    # THE EXECUTION PIPELINE
    parsed = parse_ai_output(fake_ai_thought)
    final_answer = execute_agent(parsed)

    print(f"Agent: The answer is {final_answer}")