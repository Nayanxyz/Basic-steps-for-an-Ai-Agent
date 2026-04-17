memory_db = {
    "gpu": "The user owns an RTX 3050 with 8GB of VRAM.",
    "goal": "The user wants to be in the top 0.01% of AI engineers."
}

def retrieve_memory(user_prompt):
    if "gpu" in user_prompt:
        return memory_db["gpu"]
    elif "goal" in user_prompt:
        return memory_db["goal"]
    else:
        return "No relevant memories found."

print(retrieve_memory("what is my current goal right now?"))

# if word gpu or goal is in the prompt, the result is printed from dictionary
# Retrieval-Augmented Generation (RAG)
# a micro-RAG system using Python's in keyword