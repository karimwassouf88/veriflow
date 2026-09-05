from app.rag import vector_store, reranker

def retrieve_relevant_chunks(query: str, top_k: int = 5, candidate_pool: int = 20) -> list[dict]:
    candidates = vector_store.hybrid_search(query, limit=candidate_pool)
    return reranker.rerank(query, candidates, top_k=top_k)