from fastembed.rerank.cross_encoder import TextCrossEncoder

RERANK_MODEL = "Xenova/ms-marco-MiniLM-L-6-v2"  # ~80MB, fast on CPU — bge-reranker-base (1GB+) is the upgrade path if quality matters more than speed later

_reranker: TextCrossEncoder | None = None

def _get_reranker() -> TextCrossEncoder:
    global _reranker
    if _reranker is None:
        _reranker = TextCrossEncoder(model_name=RERANK_MODEL)
    return _reranker

def rerank(query: str, candidates: list[dict], top_k: int = 5) -> list[dict]:
    if not candidates:
        return []
    pairs = [(query, c["text"]) for c in candidates]
    scores = list(_get_reranker().rerank_pairs(pairs))
    scored = sorted(zip(candidates, scores), key=lambda x: x[1], reverse=True)
    return [{**c, "rerank_score": float(s)} for c, s in scored[:top_k]]