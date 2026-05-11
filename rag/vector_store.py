from sentence_transformers import SentenceTransformer
import faiss
import numpy as np

model = SentenceTransformer('all-MiniLM-L6-v2')

docs = [
    "Sorting algorithms are important",
    "Binary search works on sorted arrays",
    "Distributed systems use multiple nodes"
]

embeddings = model.encode(docs)

index = faiss.IndexFlatL2(embeddings.shape[1])
index.add(np.array(embeddings))

def search(query):
    q = model.encode([query])
    _, idx = index.search(np.array(q), 1)
    return docs[idx[0][0]]