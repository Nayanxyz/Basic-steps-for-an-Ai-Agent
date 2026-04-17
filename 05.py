def predict_next(context_list):
    return context_list[-1] + 1

context = [1, 2, 3]

max_window = 10

while len(context) < max_window:
    new_token = predict_next(context)
    context.append(new_token)

print(context)
