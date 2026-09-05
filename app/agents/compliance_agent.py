import json
from groq import Groq
from app.core.config import settings

MODEL_NAME = "openai/gpt-oss-20b"
PROMPT_VERSION = "compliance-v1"

SYSTEM_PROMPT = """You are a procurement compliance checker. Given invoice details and relevant excerpts from company policy, determine whether this purchase complies with policy and what approval level it requires. Base your answer ONLY on the provided policy excerpts — if they don't clearly cover this case, say so honestly instead of guessing. Respond with ONLY a valid JSON object: {"compliant": boolean, "required_approval_level": string, "reasoning": string, "used_excerpts": [int]}"""

_client: Groq | None = None

def _get_client() -> Groq:
    global _client
    if _client is None:
        if not settings.groq_api_key:
            raise RuntimeError("GROQ_API_KEY is not set")
        _client = Groq(api_key=settings.groq_api_key)
    return _client

def check_compliance(invoice_fields: dict, policy_chunks: list[dict]) -> dict:
    if not policy_chunks:
        return {"compliant": False, "required_approval_level": "unknown",
                "reasoning": "No relevant policy documents have been ingested yet.", "used_excerpts": []}

    excerpt_block = "\n\n".join(f"[{i}] {c['text']}" for i, c in enumerate(policy_chunks))
    invoice_summary = "\n".join(f"{k}: {v}" for k, v in invoice_fields.items() if v is not None)

    response = _get_client().chat.completions.create(
        model=MODEL_NAME, temperature=0.1, response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Policy excerpts:\n\n{excerpt_block}\n\nInvoice details:\n{invoice_summary}"},
        ],
    )
    try:
        return json.loads(response.choices[0].message.content)
    except json.JSONDecodeError:
        return {"compliant": False, "required_approval_level": "unknown",
                "reasoning": "Could not generate a reliable compliance check.", "used_excerpts": []}