# The Vector Comparison (Cosine Similarity)
# we are going to measure the distance between two sentences. In linear algebra,
# we calculate the angle between two vectors using Cosine Similarity. A score of 1.0 means they
# are perfectly identical. A score of 0.0 means they have absolutely nothing in common.

from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer('all-MiniLM-L6-v2')

sentence_A = "I love learning about Artificial Intelligence."

sentence_B = "Machine learning is a fascinating field."

sentence_C = "I like eating pepperoni pizza."

embedding_A = model.encode(sentence_A)
embedding_B = model.encode(sentence_B)
embedding_C = model.encode(sentence_C)

score_AB = util.cos_sim(embedding_A, embedding_B)

print("Score A to B:", score_AB)
print(len(score_AB))

score_AC = util.cos_sim(embedding_A, embedding_C)

print("Score A to C:", score_AC)
print(len(score_AC))
