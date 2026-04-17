vocab = {
    "hello": 1,
    "ai": 2,
    "agent": 3
}

number_tokens = []

def tokenize_word(word):
    return vocab.get(word, 0)

prompt = "hello ai agent pizza"
words_list = prompt.split()

for word in words_list:
    # tokenize_word(word)
    number_tokens.append(tokenize_word(word))


print(number_tokens)