import json
from app.db.session import SessionLocal
from app.models.eval_run import EvalRun
from app.agents.extraction_agent import run_extraction_call, MODEL_NAME, PROMPT_VERSION
from app.eval.golden_dataset import INVOICE_GOLDEN_SET
from app.eval.metrics import score_example

def run_extraction_eval():
    all_results, total_fields, correct_fields, hallucination_count = [], 0, 0, 0

    for example in INVOICE_GOLDEN_SET:
        print(f"Running: {example['id']}...")
        extracted = run_extraction_call(example["raw_text"], temperature=0.2)
        result = score_example(example["id"], extracted, example["expected"])
        all_results.append(result)
        total_fields += result["total_fields"]
        correct_fields += result["correct_fields"]
        hallucination_count += result["hallucinations"]

    accuracy_pct = round(correct_fields / total_fields * 100, 1) if total_fields else 0.0
    hallucination_rate_pct = round(hallucination_count / total_fields * 100, 1) if total_fields else 0.0

    print("\n=== Eval Summary ===")
    print(f"Prompt version: {PROMPT_VERSION} ({MODEL_NAME})")
    print(f"Dataset: {len(INVOICE_GOLDEN_SET)} invoices, {total_fields} fields")
    print(f"Accuracy: {correct_fields}/{total_fields} ({accuracy_pct}%)")
    print(f"Hallucinations: {hallucination_count} ({hallucination_rate_pct}%)")
    for r in all_results:
        if r["mismatches"]:
            print(f"\n  {r['id']} mismatches:")
            for m in r["mismatches"]:
                print(f"    - {m}")

    db = SessionLocal()
    try:
        run = EvalRun(
            prompt_version=f"{MODEL_NAME}/{PROMPT_VERSION}", dataset_version="invoices-v1",
            total_fields=total_fields, correct_fields=correct_fields, accuracy_pct=accuracy_pct,
            hallucination_count=hallucination_count, hallucination_rate_pct=hallucination_rate_pct,
            details=json.dumps(all_results),
        )
        db.add(run); db.commit()
        print(f"\nSaved eval run {run.id}")
    finally:
        db.close()

if __name__ == "__main__":
    run_extraction_eval()