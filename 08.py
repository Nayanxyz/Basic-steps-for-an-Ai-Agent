# The ReAct Framework (Giving the AI Hands)
# the ReAct framework (Reason + Act).

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

ai_action = ["multiply", 10, 5]
print(execute_agent(ai_action))