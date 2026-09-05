import re

AMOUNT_PATTERN = re.compile(r"[\$€£]?\s?[\d,]{1,12}\.\d{2}")

def _normalize_amount(raw: str) -> float | None:
    cleaned = raw.replace("$", "").replace("€", "").replace("£", "").replace(",", "").strip()
    try:
        return float(cleaned)
    except ValueError:
        return None

def _amount_in_text(value, raw_text: str) -> bool:
    try:
        target = float(value)
    except (TypeError, ValueError):
        return False
    for match in AMOUNT_PATTERN.finditer(raw_text):
        candidate = _normalize_amount(match.group())
        if candidate is not None and abs(candidate - target) < 0.01:
            return True
    return False

def _values_match(a, b, field_name: str) -> bool:
    if a is None or b is None:
        return False
    if field_name == "total_amount":
        try:
            return abs(float(a) - float(b)) < 0.01
        except (TypeError, ValueError):
            return False
    return str(a).strip().lower() == str(b).strip().lower()

def score_extraction(fields: list[str], run_1: dict, run_2: dict, raw_text: str) -> dict:
    """
    Combines two signals per field:
    - self-consistency: do two independent LLM calls agree?
    - deterministic cross-check: for total_amount only, does the value actually
      appear in the raw document text via regex? (the one field where a cheap,
      non-LLM ground-truth check is realistic)
    """
    results = {}
    for field_name in fields:
        v1, v2 = run_1.get(field_name), run_2.get(field_name)
        if v1 is None and v2 is None:
            results[field_name] = (None, 0.0)
            continue
        value = v1 if v1 is not None else v2
        confidence = 0.4
        if _values_match(v1, v2, field_name):
            confidence += 0.35
        if field_name == "total_amount" and _amount_in_text(value, raw_text):
            confidence += 0.25
        results[field_name] = (value, round(min(confidence, 1.0), 2))
    return results