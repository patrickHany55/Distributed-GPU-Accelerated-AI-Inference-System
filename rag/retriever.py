from rag.vector_store import search

def retrieve_context(query):
    return search(query)