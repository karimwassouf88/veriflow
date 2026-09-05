import uuid
from qdrant_client import QdrantClient, models
from app.core.config import settings

COLLECTION_NAME = "policy_chunks"
DENSE_MODEL = "BAAI/bge-base-en-v1.5"   # 768-dim, good quality/speed balance for local CPU use
SPARSE_MODEL = "Qdrant/bm25"             # true statistical BM25, no neural model needed
DENSE_SIZE = 768

_client: QdrantClient | None = None

def get_client() -> QdrantClient:
    global _client
    if _client is None:
        _client = QdrantClient(url=settings.qdrant_url, api_key=settings.qdrant_api_key or None)
    return _client

def ensure_collection() -> None:
    client = get_client()
    if not client.collection_exists(COLLECTION_NAME):
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config={"dense": models.VectorParams(size=DENSE_SIZE, distance=models.Distance.COSINE)},
            sparse_vectors_config={"sparse": models.SparseVectorParams(modifier=models.Modifier.IDF)},
        )

def delete_document_chunks(document_id: uuid.UUID) -> None:
    ensure_collection()
    client = get_client()
    client.delete(
        collection_name=COLLECTION_NAME,
        points_selector=models.FilterSelector(
            filter=models.Filter(must=[models.FieldCondition(
                key="document_id", match=models.MatchValue(value=str(document_id))
            )])
        ),
    )

def upsert_chunks(document_id: uuid.UUID, filename: str, chunks: list[str]) -> int:
    ensure_collection()
    client = get_client()
    points = [
        models.PointStruct(
            id=str(uuid.uuid4()),
            vector={
                "dense": models.Document(text=chunk, model=DENSE_MODEL),
                "sparse": models.Document(text=chunk, model=SPARSE_MODEL),
            },
            payload={"document_id": str(document_id), "filename": filename, "chunk_index": idx, "text": chunk},
        )
        for idx, chunk in enumerate(chunks)
    ]
    client.upsert(collection_name=COLLECTION_NAME, points=points)
    return len(points)

def hybrid_search(query: str, limit: int = 20) -> list[dict]:
    ensure_collection()
    client = get_client()
    response = client.query_points(
        collection_name=COLLECTION_NAME,
        prefetch=[
            models.Prefetch(query=models.Document(text=query, model=DENSE_MODEL), using="dense", limit=limit),
            models.Prefetch(query=models.Document(text=query, model=SPARSE_MODEL), using="sparse", limit=limit),
        ],
        query=models.FusionQuery(fusion=models.Fusion.RRF),
        limit=limit,
    )
    return [
        {"text": p.payload["text"], "document_id": p.payload["document_id"],
         "filename": p.payload["filename"], "chunk_index": p.payload["chunk_index"], "score": p.score}
        for p in response.points
    ]