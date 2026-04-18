import json as js

ai_output_string = '{"action": "multiply", "parameters": [12, 4]}'
parsed_data = js.loads(ai_output_string)


def multi(a,b):
    multiplication = a * b
    return multiplication



keys = parsed_data.keys()

nums = parsed_data["parameters"]


print(multi(nums[0], nums[1]))