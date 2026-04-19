# Embeddings
# An embedding is a tool that takes an English sentence and turns it into
# an array of thousands of numbers (coordinates).
# We store these coordinates in a Vector Database.

from sentence_transformers import SentenceTransformer

model = SentenceTransformer('all-MiniLM-L6-v2')

text = "I love learning about Artificial Intelligence."

embeddings = model.encode(text)

print(embeddings)
print(len(embeddings))