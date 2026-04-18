import json as js

broken_ai_string = '{"action": "multiply", "parameters": [12, 4}'

def multi(a,b):
    multiplication = a * b
    return multiplication


def safe_parse(json_string):
    try:
        parsed = js.loads(json_string)
        return parsed
    except js.JSONDecodeError:
        print("Warning: AI generated invalid JSON.")
        return {"action": "error", "parameters": [0, 0]}

parsed_data = safe_parse(broken_ai_string)

nums = parsed_data["parameters"]


print(multi(nums[0], nums[1]))