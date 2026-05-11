from rag.vector_store import search
from llm.inference import generate_response

def process_query(query):

    context = search(query)

    prompt = f"""
Answer clearly.

Context:
{context}

Question:
{query}

Answer:
"""

    result = generate_response(prompt)

    return result