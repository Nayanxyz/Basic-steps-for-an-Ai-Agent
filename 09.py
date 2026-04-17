# Parser
# A parser is a piece of code that takes the messy, human-readable text from the AI
# and mathematically slices it down into strict, formatted data (like a list) that your tools can actually use

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
    command = chopped_list[0]
    num1 = int(chopped_list[1])
    num2 = int(chopped_list[2])
    return [command, num1, num2]

raw_ai_text = "ACTION: add | 40 | 12"

parsed = parse_ai_output(raw_ai_text)
final = execute_agent(parsed)
print(final)