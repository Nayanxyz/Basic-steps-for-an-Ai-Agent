vocab = {
    "hello": 1,
    "ai": 2,
    "agent": 3
}

def tokenize_word(word):
    return vocab.get(word, 0)

print(tokenize_word("ai"))
print(tokenize_word("pizza"))



