import json
from groq import Groq
from app.core.config import settings

MODEL_NAME = "openai/gpt-oss-20b"
PROMPT_VERSION = "policy-qa-v1"

SYSTEM_PROMPT = """You are a company policy assistant. Answer the user's question using ONLY the provided policy excerpts. If the excerpts don't contain enough information to answer confidently, say so explicitly instead of guessing. Respond with ONLY a valid JSON object: {"answer": string, "used_excerpts": [int], "answerable": boolean}"""

_client: Groq | None = None

def _get_client() -> Groq:
    global _client
    if _client is None:
        if not settings.groq_api_key:
            raise RuntimeError("GROQ_API_KEY is not set")
        _client = Groq(api_key=settings.groq_api_key)
    return _client

def answer_from_chunks(query: str, chunks: list[dict]) -> dict:
    if not chunks:
        return {"answer": "No relevant policy documents have been ingested yet.", "used_excerpts": [], "answerable": False}

    excerpt_block = "\n\n".join(f"[{i}] {c['text']}" for i, c in enumerate(chunks))
    response = _get_client().chat.completions.create(
        model=MODEL_NAME,
        temperature=0.1,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Policy excerpts:\n\n{excerpt_block}\n\nQuestion: {query}"},
        ],
    )
    try:
        return json.loads(response.choices[0].message.content)
    except json.JSONDecodeError:
        return {"answer": "Could not generate a reliable answer.", "used_excerpts": [], "answerable": False}