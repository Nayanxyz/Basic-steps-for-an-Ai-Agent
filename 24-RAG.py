# The Vector Database (ChromaDB)
# he beautiful thing about ChromaDB is that it actually handles the sentence-transformers embedding
# math automatically under the hood, so you don't even have to use .encode() manually anymore.

import chromadb

client = chromadb.Client()

collection = client.create_collection(name="test_collection")

sentence_A = "I love learning about Artificial Intelligence."

sentence_B = "Machine learning is a fascinating field."

sentence_C = "I like eating pepperoni pizza."

collection.add(
    documents= [sentence_A, sentence_B, sentence_C],
    ids=["id1", "id2", "id3"]
)

results = collection.query(
query_texts=["I want to read about computers."],
    n_results=1
)

print(results)