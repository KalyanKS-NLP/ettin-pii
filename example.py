"""
End-to-end demo of ettin-pii featuring Models, Redaction, Batching, Stats, and Exports.
"""
from ettin_pii import PIIDetector

def main():
    # 1. Initialize PIIDetector using the default "small" (68M) model
    # (Or choose "tiny" for 32M or "nano" for 17M for ultra-fast inference)
    print("Initializing PIIDetector (model: small)...")
    detector = PIIDetector(model="small", confidence_threshold=0.6)

    sample = (
        "Customer Alex Murphy (SSN: 987-65-4321) requested a password reset. "
        "Contact them at alex.murphy@corp.org or call 415-555-0199."
    )

    print("\n--- 1. Single Text Detection ---")
    result = detector.detect(sample)
    print(f"Detected {result.num_entities} entities:")
    for ent in result.entities:
        print(f"  [{ent.label}] '{ent.text}' (Confidence: {ent.score:.2%})")

    print("\n--- 2. Multi-Strategy Redaction ---")
    print("Replace (Tags)       :", result.redact(strategy="replace"))
    print("Mask (Full)          :", result.redact(strategy="mask", mask_mode="full"))
    print("Mask (Alternate)     :", result.redact(strategy="mask", mask_mode="alternate"))
    print("Mask (First Only)    :", result.redact(strategy="mask", mask_mode="first_only"))
    print("Fake (Synthetic PII) :", result.redact(strategy="fake"))
    print("Custom Mapping       :", result.redact(strategy="custom", mapping={"name": "[CONFIDENTIAL_USER]"}))

    print("\n--- 3. Statistics & Density ---")
    print(result.statistics)

    print("\n--- 4. Batch Detection (BatchDetectionResult) ---")
    batch_data = [
        "Reach Sarah at sarah@dev.io",
        "No sensitive data here.",
        "Server IP is 192.168.1.10 assigned to Dave.",
    ]
    batch_results = detector.detect(batch_data, batch_size=2)
    print(f"Total texts in batch: {len(batch_results)}")
    print("Batch Statistics   :", batch_results.statistics)
    print("All Redacted Texts :", batch_results.redacted_texts)

    print("\n--- 5. Single & Combined Batch Exports ---")
    print("Single Result JSON:\n", result.to_json(indent=2))

    # Combined Batch DataFrame Export
    batch_df = batch_results.to_dataframe()
    print("\nCombined Batch DataFrame:\n", batch_df[["text_index", "label", "text", "score", "source_text"]])

if __name__ == "__main__":
    main()

