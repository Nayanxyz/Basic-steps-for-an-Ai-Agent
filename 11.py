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

