from app.services.confidence_scoring import score_extraction

def test_matching_values_get_high_confidence():
    run_1 = {"vendor_name": "Acme Corp", "total_amount": 150.00}
    run_2 = {"vendor_name": "Acme Corp", "total_amount": 150.00}
    result = score_extraction(["vendor_name", "total_amount"], run_1, run_2, "Total: $150.00")
    assert result["vendor_name"][1] >= 0.75
    assert result["total_amount"][1] == 1.0

def test_disagreeing_values_get_baseline_confidence():
    run_1 = {"vendor_name": "Acme Corp"}
    run_2 = {"vendor_name": "Acme Inc"}
    result = score_extraction(["vendor_name"], run_1, run_2, "")
    assert result["vendor_name"][1] == 0.4

def test_missing_value_gets_zero_confidence():
    result = score_extraction(["due_date"], {"due_date": None}, {"due_date": None}, "")
    assert result["due_date"] == (None, 0.0)