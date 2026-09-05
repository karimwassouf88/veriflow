def _normalize(value):
    if value is None:
        return None
    return str(value).strip().lower()

def _fields_match(field_name: str, extracted, expected) -> bool:
    if expected is None:
        return extracted is None  # correct only if the model also said null
    if extracted is None:
        return False
    if field_name == "total_amount":
        try:
            return abs(float(extracted) - float(expected)) < 0.01
        except (TypeError, ValueError):
            return False
    return _normalize(extracted) == _normalize(expected)

def score_example(example_id: str, extracted: dict, expected: dict) -> dict:
    total_fields = 0
    correct_fields = 0
    hallucinations = 0
    mismatches = []

    for field_name, expected_value in expected.items():
        total_fields += 1
        extracted_value = extracted.get(field_name)
        if _fields_match(field_name, extracted_value, expected_value):
            correct_fields += 1
        else:
            mismatches.append(f"{field_name}: expected={expected_value!r}, got={extracted_value!r}")
        if expected_value is None and extracted_value is not None:
            hallucinations += 1  # model stated something as fact that wasn't actually there

    return {"id": example_id, "total_fields": total_fields, "correct_fields": correct_fields,
            "hallucinations": hallucinations, "mismatches": mismatches}