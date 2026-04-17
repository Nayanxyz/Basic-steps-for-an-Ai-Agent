def predict_next(context_list):
    if context_list[-1] == 5:
        return 99 # The Stop Token
    else:
        return context_list[-1] + 1
context = [1, 2, 3]
max_window = 10

while len(context) < max_window:
    new_token = predict_next(context)
    if new_token == 99:
        break
    else:
        context.append(new_token)

print(context)

# Retrieval-Augmented Generation (RAG)
# RAG works like an open-book test. Before the AI answers your question,
# a separate piece of code searches your personal database, pulls out the
# exact document you need, and silently pastes it into the AI's context window.