# ettin-pii: Production-Ready PII Detection & Redaction Toolkit

<p align="left">
  <a href="https://pypi.org/project/ettin-pii/"><img src="https://img.shields.io/pypi/v/ettin-pii.svg?color=blue" alt="PyPI version"></a>
  <a href="https://pypi.org/project/ettin-pii/"><img src="https://img.shields.io/badge/python->=3.10-blue.svg" alt="Python versions"></a>
  <a href="https://github.com/KalyanKS-NLP/ettin-pii/actions/workflows/tests.yml"><img src="https://github.com/KalyanKS-NLP/ettin-pii/actions/workflows/tests.yml/badge.svg" alt="CI Tests"></a>
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"></a>
  <a href="https://huggingface.co/kalyan-ks"><img src="https://img.shields.io/badge/%F0%9F%A4%97%20Hugging%20Face-Models-orange" alt="Hugging Face Models"></a>
</p>

A high-performance Python PII detection and anonymization library powered by the **Ettin Nemotron PII** model family (`kalyan-ks/ettin-*-nemotron-pii`), detecting **50+ Personally Identifiable Information (PII) entity types** across healthcare, finance, legal, and cyber domains.

---

## Supported Model Family

| Model Alias | Hugging Face Repository | Parameter Size | Best For |
| :--- | :--- | :--- | :--- |
| **`"small"`** *(Default)* | [`kalyan-ks/ettin-68m-nemotron-pii`](https://huggingface.co/kalyan-ks/ettin-68m-nemotron-pii) | ~68.5M | Maximum accuracy (~96.27% F1), server workloads, audit pipelines |
| **`"tiny"`** | [`kalyan-ks/ettin-32m-nemotron-pii`](https://huggingface.co/kalyan-ks/ettin-32m-nemotron-pii) | ~32M | Balanced speed and accuracy for real-time CPU processing |
| **`"nano"`** | [`kalyan-ks/ettin-17m-nemotron-pii`](https://huggingface.co/kalyan-ks/ettin-17m-nemotron-pii) | ~17.5M | Ultra-low latency, serverless functions (AWS Lambda), edge devices |

---

## Features

- **Structured Result Objects:** Immutable `Entity`, `DetectionResult`, and `BatchDetectionResult` dataclasses.
- **4 Anonymization Strategies:**
  - `replace`: Tag replacements like `<EMAIL>`, `<NAME>`, `<SSN>`.
  - `mask`: Character masking with 3 sub-modes: `full` (`****`), `alternate` (`a*e*.*u*p*y`), and `first_only` (`A*** M*****`).
  - `fake`: Format-preserving synthetic scramble preserving symbols, digits, and casing.
  - `custom`: Dictionary mapping for specific entity types with automatic safe fallback.
- **Unified Detection Pipeline:** Polymorphic `.detect()` method returning single or batch containers with mini-batch inference and adjacent entity stitching.
- **Summary Metrics & Density:** `.statistics` reporting entity counts, unique types, and text density.
- **Multi-Format Exports:** `.to_json()`, `.to_csv()`, `.to_dataframe()`, and `.to_dict()` on both single and batch results.
- **CLI Tool:** `ettin-pii` commands for `detect`, `redact`, and `stats`.

---

## Installation

Using `uv` (recommended):
```bash
uv add ettin-pii
```

Or standard `pip`:
```bash
pip install ettin-pii
```

---

## Quickstart

```python
from ettin_pii import PIIDetector

# Initialize detector (model="small", "tiny", or "nano")
detector = PIIDetector(model="small", confidence_threshold=0.6)

# 1. Single text detection
result = detector.detect("Customer Alex Murphy (SSN: 987-65-4321) contacted us at alex.murphy@corp.org")
print(f"Found {result.num_entities} PII entities")

# 2. Multi-strategy redaction
print(result.redact(strategy="replace"))
# Output: Customer <NAME> (SSN: <SSN>) contacted us at <EMAIL>

print(result.redact(strategy="mask", mask_mode="first_only"))
# Output: Customer A*** M***** (SSN: 9**-**-****) contacted us at a***.m*****@corp.org

# 3. Export to Pandas DataFrame
df = result.to_dataframe()
print(df)
```

---

## Command Line Interface (CLI)

```bash
# 1. Detect PII inline
ettin-pii detect "Call Dr. John at 555-0144"

# 2. Redact with tiny model and mask strategy
ettin-pii redact "Call Dr. John at 555-0144" --model tiny --strategy mask --mask-mode first_only

# 3. Redact file and save to disk
ettin-pii redact input.txt --output sanitized.txt

# 4. Generate summary statistics
ettin-pii stats "Customer John Doe, email: john@gmail.com, phone: 555-1234"

# 5. Generate summary statistics with verbose entity list
ettin-pii stats "Customer John Doe, email: john@gmail.com, phone: 555-1234" -v

# 6. Generate batch statistics across multi-line file
ettin-pii stats records.txt --batch

# 7. Redact multi-line records in batch mode
ettin-pii redact records.txt --batch --output clean_records.txt
```

---

## License

MIT License.
