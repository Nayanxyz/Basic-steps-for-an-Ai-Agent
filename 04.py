# Autoregressive Generation loop  // built the heartbeat of an AI agent.

def predict_next(context_list):
    return context_list[-1] + 1

context = [1, 2, 3]

for i in range(3):
    new_token = predict_next(context)
    context.append(new_token)

print(context)

# Every time the loop runs, the context list gets longer.
# Run it 10 times? The list has 13 numbers.
# Run it 1,000 times? The list has 1,003 numbers.
# If that list gets too long, the GPU will completely run out of memory and crash.
# The maximum number of tokens an AI can hold in its memory at one time is called its Context Window.