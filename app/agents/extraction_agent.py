import json
from groq import Groq
from app.core.config import settings

MODEL_NAME = "openai/gpt-oss-20b"
PROMPT_VERSION = "extraction-v2"  # schema changed, so the version bumps — same principle as the blueprint's prompt versioning

SYSTEM_PROMPT = """You are a precise invoice data extraction system. Extract only what is explicitly stated in the document text. Never guess or infer values that are not present. Respond with ONLY a valid JSON object matching this exact schema, no other text:

{
  "vendor_name": string or null,
  "invoice_number": string or null,
  "invoice_date": string "YYYY-MM-DD" or null,
  "due_date": string "YYYY-MM-DD" or null,
  "total_amount": number or null,
  "currency": string (3-letter ISO code) or null,
  "po_reference": string or null
}

If a field is not clearly present in the text, use null. Do not fabricate values."""

_client: Groq | None = None

def _get_client() -> Groq:
    global _client
    if _client is None:
        if not settings.groq_api_key:
            raise RuntimeError("GROQ_API_KEY is not set — add it to your .env file")
        _client = Groq(api_key=settings.groq_api_key)
    return _client

def run_extraction_call(raw_text: str, temperature: float) -> dict:
    client = _get_client()
    response = client.chat.completions.create(
        model=MODEL_NAME,
        temperature=temperature,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Document text:\n\n{raw_text[:12000]}"},
        ],
    )
    try:
        return json.loads(response.choices[0].message.content)
    except json.JSONDecodeError:
        return {}