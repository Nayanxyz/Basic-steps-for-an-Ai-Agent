def add_numbers(a, b):
    return a + b

def multiply_numbers(a, b):
    return a * b

def execute_agent(action_list):
    if action_list[0] == "add":
        addition = add_numbers(action_list[1], action_list[2])
        return addition

    elif action_list[0] == "multiply":
        multiply = multiply_numbers(action_list[1], action_list[2])
        return multiply



def parse_ai_output(text):
    chopped_list = text.replace("ACTION: ", "").split(" | ")
    command = chopped_list[0].strip()
    num1 = int(chopped_list[1])
    num2 = int(chopped_list[2])
    return [command, num1, num2]


while True:
    user_input = input("You: ")  # Ask the user

    if user_input == "exit":
        print("Shutting down agent...")
        break

    elif user_input == "add 10 5":  # No extra spaces!
        fake_ai_thought = "ACTION: add | 10 | 5"

    elif user_input == "multiply 10 5":
        fake_ai_thought = "ACTION: multiply | 10 | 5"

    else:
        # If they type "pizza", we catch it here.
        print("Agent: I don't know how to do that yet.")
        continue  # Instantly jumps back to 'input("You: ")', saving the code from crashing!

    # --- The Execution Pipeline ---
    # This only runs if they typed a valid command.
    parsed = parse_ai_output(fake_ai_thought)
    final_answer = execute_agent(parsed)

    # Print the actual answer INSIDE the loop so the user sees it.
    print(f"Agent: The answer is {final_answer}")