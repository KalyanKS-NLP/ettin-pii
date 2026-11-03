# `ettin-pii` Comprehensive User Guide & Library Reference

Welcome to the official, detailed documentation for **`ettin-pii`**, a production-grade Python library for PII detection, and anonymization.

---

## Table of Contents

1. [Architecture & Model Family](#1-architecture--model-family)
2. [Installation & Requirements](#2-installation--requirements)
3. [Core Detection Pipeline](#3-core-detection-pipeline)
   - [Initializing `PIIDetector`](#initializing-piidetector)
   - [Single-Text Detection](#single-text-detection)
   - [High-Volume Batch Detection](#high-volume-batch-detection)
   - [Token Stitching & Whitespace Alignment](#token-stitching--whitespace-alignment)
4. [Mastering the 4 Redaction Strategies](#4-mastering-the-4-redaction-strategies)
   - [Strategy 1: `replace` (Tag Replacement)](#strategy-1-replace-tag-replacement)
   - [Strategy 2: `mask` (Asterisk / Partial Masking)](#strategy-2-mask-asterisk--partial-masking)
   - [Strategy 3: `fake` (Synthetic Format-Preserving Data)](#strategy-3-fake-synthetic-format-preserving-data)
   - [Strategy 4: `custom` (Dictionary Mapping)](#strategy-4-custom-dictionary-mapping)
5. [Privacy Auditing & Quantitative Statistics](#5-privacy-auditing--quantitative-statistics)
   - [Single Result Statistics](#single-result-statistics)
   - [Batch-Level Dataset Statistics](#batch-level-dataset-statistics)
6. [Multi-Format Data Exporters](#6-multi-format-data-exporters)
7. [Command Line Interface (CLI) Manual](#7-command-line-interface-cli-manual)
8. [Hardware Acceleration & Performance Tips](#8-hardware-acceleration--performance-tips)
9. [Frequently Asked Questions (FAQ)](#9-frequently-asked-questions-faq)

---

## 1. Architecture & Model Family

`ettin-pii` is built on top of the **Ettin Nemotron PII** model family trained by [Kalyan KS](https://huggingface.co/kalyan-ks). These models were, fine-tuned on NVIDIA's extensive **Nemotron-PII** dataset. These models can recognize over **50+ sensitive entity classes** spanning financial, medical, legal, identity, and cybersecurity domains (names, emails, SSNs, credit cards, passport numbers, API keys, IP addresses, dates of birth, etc.).

### Supported Model Sizes

| Model Key | Hugging Face Repository | Parameters | Recommended Hardware | Primary Use Case |
| :--- | :--- | :--- | :--- | :--- |
| **`"small"`** *(Default)* | [`kalyan-ks/ettin-68m-nemotron-pii`](https://huggingface.co/kalyan-ks/ettin-68m-nemotron-pii) | ~68.5M | GPU or multi-core CPU | Maximum detection accuracy (~96.27% F1), audit pipelines, high-stakes compliance |
| **`"tiny"`** | [`kalyan-ks/ettin-32m-nemotron-pii`](https://huggingface.co/kalyan-ks/ettin-32m-nemotron-pii) | ~32M | Standard CPU | Balanced speed and accuracy for real-time customer chats and web backends |
| **`"nano"`** | [`kalyan-ks/ettin-17m-nemotron-pii`](https://huggingface.co/kalyan-ks/ettin-17m-nemotron-pii) | ~17.5M | CPU / Low-power devices | Ultra-low latency, serverless functions (AWS Lambda), IoT, edge microcontrollers |

> [!NOTE]
> All three models are hosted publicly on Hugging Face. When you initialize a model for the first time, `ettin-pii` downloads the weights automatically into your Hugging Face cache and reuses them locally forever with zero network overhead.

---

## 2. Installation & Requirements

### Prerequisites
- Python **>= 3.10**
- PyTorch **>= 2.0.0**
- Transformers **>= 4.40.0**
- Pandas **>= 2.0.0**

### Installation

Using `uv` (recommended):
```bash
uv add ettin-pii
```

Using standard `pip`:
```bash
pip install ettin-pii
```

To verify the installation:
```python
import ettin_pii
print(ettin_pii.__version__)  # Output: 0.1.0
```

---

## 3. Core Detection Pipeline

### Initializing `PIIDetector`

Import `PIIDetector` directly from the top-level package:

```python
from ettin_pii import PIIDetector

detector = PIIDetector(
    model="small",               # "small" (68M), "tiny" (32M), or "nano" (17M)
    device=None,                 # "cuda", "cpu", or None (auto-detects CUDA GPU)
    batch_size=16,               # Default mini-batch size for multi-string inference
    confidence_threshold=0.50    # Minimum confidence score (0.0 to 1.0)
)
```

#### Initialization Parameters:

- **`model`** (*str, optional*): Selects the model size (`"small"`, `"tiny"`, or `"nano"`). Defaults to `"small"`. Invalid values raise a clear `ValueError`.
- **`device`** (*str, optional*): Choose `"cuda"` or `"cpu"`. When set to `None` (default), the detector automatically enables GPU acceleration if `torch.cuda.is_available()` is `True`.
- **`batch_size`** (*int, optional*): Batch chunk size passed to PyTorch when processing lists of strings. Defaults to `16`.
- **`confidence_threshold`** (*float, optional*): Filters out low-confidence predictions. Defaults to `0.50`.

---

### Single-Text Detection

Pass any string to `.detect()`:

```python
text = "Patient John Doe (DOB: 12/05/1980) visited our clinic. Contact him at john.doe@med.org."
result = detector.detect(text)

print(f"Detected {result.num_entities} PII entities:")
for entity in result.entities:
    print(f" - [{entity.label}] '{entity.text}' (Score: {entity.score:.2%}, Offsets: {entity.start}-{entity.end})")
```

#### The `Entity` Object
Each detected item inside `result.entities` is an immutable `Entity` dataclass:
- `entity.text` (*str*): The exact entity substring (e.g., `'john.doe@med.org'`).
- `entity.label` (*str*): The recognized PII class (e.g., `'email'`, `'first_name'`, `'date'`).
- `entity.score` (*float*): The model's confidence probability between `0.0` and `1.0`.
- `entity.start` (*int*): Zero-based start character offset in the source string.
- `entity.end` (*int*): End character offset in the source string.
- `entity.length` (*int*): Span length in characters (`end - start`).

#### The `DetectionResult` Container
- `result.text` (*str*): The original input text.
- `result.entities` (*List[Entity]*): List of detected entities.
- `result.has_pii` (*bool*): `True` if one or more entities were detected.
- `result.num_entities` (*int*): Count of detected entities.
- `result.redacted_text` (*str*): Convenience property returning text with default `<TAG>` redactions.
- `result.statistics` (*dict*): Quantitative metrics dictionary.

---

### High-Volume Batch Detection

To process multiple documents, messages, or rows simultaneously, pass a `List[str]` directly to the **same** `.detect()` method:

```python
documents = [
    "Customer Sarah Connor requested account deletion.",
    "System status normal. CPU load 12%.",
    "Forward invoice to accounting@corp.com or call 555-0199.",
]

# detect() automatically returns a BatchDetectionResult
batch_result = detector.detect(documents, batch_size=4)

print(f"Total documents processed: {len(batch_result)}")
print(f"Total sensitive entities found: {batch_result.total_entities}")
```


---

## 4. Mastering the 4 Redaction Strategies

`ettin-pii` provides four purpose-built redaction strategies accessible via `result.redact()` or `batch_result.redact()`.

```python
sample = "Contact Dr. Kalyan at kalyan.ks@yahoo.com or call 555-0199."
result = detector.detect(sample)
```

---

### Strategy 1: `replace` (Tag Replacement)

Replaces sensitive spans with descriptive uppercase tags reflecting the detected entity label:

```python
print(result.redact(strategy="replace"))
```
**Output:**
```text
Contact Dr. <FIRST_NAME> at <EMAIL> or call <PHONE_NUMBER>.
```
* **Best For:** Regulatory redaction, preparing training data for LLMs, and privacy-preserving documentation where readers still need to know what kind of entity was removed.

---

### Strategy 2: `mask` (Asterisk / Partial Masking)

Replaces characters with a mask character (default: `*`) using one of three customizable sub-modes:

#### Mode A: `"full"` (Default)
Masks every character in the span:
```python
print(result.redact(strategy="mask", mask_mode="full"))
```
**Output:**
```text
Contact Dr. ****** at ******************* or call ********.
```

#### Mode B: `"alternate"`
Masks alternating characters while leaving punctuation (`@`, `.`, `-`) intact for readable hints:
```python
print(result.redact(strategy="mask", mask_mode="alternate"))
```
**Output:**
```text
Contact Dr. K*l*a* at k*l*a*.*s*@y*h*o*.c*m or call 5*5-0*9*.
```

#### Mode C: `"first_only"`
Keeps the first letter of each word and masks remaining letters:
```python
print(result.redact(strategy="mask", mask_mode="first_only"))
```
**Output:**
```text
Contact Dr. K***** at k****************** or call 5***********.
```

#### Custom Masking Character
You can specify any custom character using `mask_char`:
```python
print(result.redact(strategy="mask", mask_char="█", mask_mode="full"))
# Output: Contact Dr. ██████ at ███████████████████ or call ████████.
```

---

### Strategy 3: `fake` (Synthetic Format-Preserving Data)

Generates pseudo-random synthetic characters while **preserving the exact original formatting**:
- Capital letters become random uppercase letters (`A-Z`).
- Lowercase letters become random lowercase letters (`a-z`).
- Digits become random numbers (`0-9`).
- Punctuation (`@`, `.`, `-`, spaces) is completely preserved.

```python
print(result.redact(strategy="fake"))
```
**Output:**
```text
Contact Dr. Wxebql at jzvfha.rm@mknvd.yom or call 843-9812.
```
* **Best For:** Staging, integration testing, QA database seeding, and downstream NLP pipelines that require syntactically valid sentences without exposing real customer data.

---

### Strategy 4: `custom` (Dictionary Mapping)

Allows you to supply a custom Python dictionary mapping entity labels to custom placeholder values:

```python
custom_map = {
    "email": "[REDACTED_EMAIL_ADDRESS]",
    "first_name": "[AUTHORIZED_DOCTOR]",
}

print(result.redact(strategy="custom", mapping=custom_map))
```
**Output:**
```text
Contact Dr. [AUTHORIZED_DOCTOR] at [REDACTED_EMAIL_ADDRESS] or call <PHONE_NUMBER>.
```

> [!TIP]
> **Automatic Safety Fallback:** If the model detects an entity type that was not included in your custom mapping dictionary (e.g., `phone_number` above), `ettin-pii` automatically falls back to `<PHONE_NUMBER>` so sensitive data never accidentally leaks.

---

## 5. Privacy Auditing & Quantitative Statistics

### Single Result Statistics

Calling `result.statistics` generates quantitative metrics describing the privacy exposure of a document:

```python
result = detector.detect("John Doe, email: john@gmail.com, SSN: 123-45-6789")
print(result.statistics)
```

**Output:**
```python
{
    "total_entities": 3,
    "unique_entity_types": 3,
    "entity_counts": {
        "first_name": 1,
        "email": 1,
        "ssn": 1
    },
    "density": 0.4915,              # 49.15% of the total characters are PII
    "average_confidence": 0.9386    # 93.86% average model confidence
}
```

---

### Batch-Level Dataset Statistics

When analyzing datasets or multi-row files, `batch_result.statistics` computes dataset-wide exposure:

```python
batch_result = detector.detect([
    "Reach Sarah at sarah@dev.io",
    "System reboot initiated.",
    "Dave's phone is 555-0199 and SSN is 987-65-4321.",
])
print(batch_result.statistics)
```

**Output:**
```python
{
    "total_texts": 3,
    "texts_with_pii": 2,          # 2 out of 3 records contain sensitive data
    "total_entities": 4,          # 4 total PII instances detected
    "unique_entity_types": 4,     # first_name, email, phone_number, ssn
    "entity_counts": {
        "first_name": 2,
        "email": 1,
        "phone_number": 1,
        "ssn": 1
    }
}
```

---

## 6. Multi-Format Data Exporters

Both single and batch results support native export methods to JSON, CSV, dictionary, and Pandas DataFrames.

### Single Result Exports

```python
# 1. Convert to Python dict
data_dict = result.to_dict()

# 2. Serialize to JSON string or write to file
json_str = result.to_json(indent=2)
result.to_json("audit_report.json")

# 3. Write detected entities to CSV
result.to_csv("entities.csv")

# 4. Convert directly to a Pandas DataFrame
df = result.to_dataframe()
print(df)
```

**Sample Single DataFrame:**
| label | text | score | start | end | length |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `first_name` | John | 0.9856 | 0 | 4 | 4 |
| `email` | john@gmail.com | 0.9906 | 18 | 32 | 14 |
| `ssn` | 123-45-6789 | 0.9660 | 39 | 50 | 11 |

---

### Batch Result Exports

For batch results, exporters include `text_index` and `source_text` so you can trace every entity back to its originating record:

```python
# 1. Export combined batch to CSV
batch_result.to_csv("all_detected_records.csv")

# 2. Export combined batch to JSON
batch_result.to_json("batch_audit.json")

# 3. Combined Batch DataFrame
batch_df = batch_result.to_dataframe()
print(batch_df[["text_index", "label", "text", "source_text"]])
```

**Sample Batch DataFrame:**
| text_index | label | text | score | source_text |
| :--- | :--- | :--- | :--- | :--- |
| 0 | `first_name` | Sarah | 0.98 | Reach Sarah at sarah@dev.io |
| 0 | `email` | sarah@dev.io | 0.99 | Reach Sarah at sarah@dev.io |
| 2 | `first_name` | Dave | 0.95 | Server IP assigned to Dave. |

---

## 7. Command Line Interface (CLI) Manual

`ettin-pii` provides a command-line tool accessible in your terminal after installation.

### Subcommands

#### 1. `ettin-pii detect`
Scans raw text or files for PII:
```bash
# Scan raw text inline
ettin-pii detect "Dr. Kalyan at kalyan.ks@yahoo.com"

# Scan with tiny model and export to JSON
ettin-pii detect document.txt --model tiny -o entities.json

# Scan line-delimited records in batch mode
ettin-pii detect records.txt --batch -o batch_entities.json
```

#### 2. `ettin-pii redact`
Sanitizes raw text or files using any strategy:
```bash
# Default tag replacement
ettin-pii redact "Call John at 555-0199"

# Masking with first letter visible
ettin-pii redact "Call John at 555-0199" --strategy mask --mask-mode first_only

# Synthetic format-preserving scrambling
ettin-pii redact "Call John at 555-0199" --strategy fake

# Batch file redaction saving output to clean file
ettin-pii redact records.txt --batch --output clean_records.txt
```

#### 3. `ettin-pii stats`
Generates privacy audit and density reports:
```bash
# Compact single-text summary
ettin-pii stats "Customer John Doe, email: john@gmail.com"

# Verbose inspection (-v) showing exact matched values
ettin-pii stats "Customer John Doe, email: john@gmail.com" -v

# Batch statistics over multi-line dataset
ettin-pii stats customer_messages.txt --batch

# Batch statistics with itemized record breakdown
ettin-pii stats customer_messages.txt --batch -v
```

---

## 8. Hardware Acceleration & Performance Tips

1. **Automatic GPU Acceleration:**
   If PyTorch detects an NVIDIA GPU with CUDA, `ettin-pii` automatically routes inference to the GPU. You do not need to configure anything.
2. **Model Selection Tradeoffs:**
   - For real-time user-facing typing or latency-critical APIs: use `model="nano"` (17M parameters, ~5–10ms per sentence on CPU).
   - For batch document processing or legal audits: use `model="small"` (68M parameters, maximum precision).
3. **Batch Size Tuning:**
   When running `.detect(list_of_texts)`:
   - On CPU: `batch_size=16` or `32` is optimal.
   - On GPU: You can comfortably increase to `batch_size=64` or `128` for throughput up to thousands of sentences per minute.

---

## 9. Frequently Asked Questions (FAQ)

**Q: Do I need internet access to run `ettin-pii`?**  
**A:** Only on the very first execution to download the model weights (~35MB to ~130MB). Afterwards, `ettin-pii` works 100% offline without sending any data over the internet.

**Q: Does `ettin-pii` send my text to any external server?**  
**A:** No. Inference runs completely locally on your machine. No text or metadata ever leaves your environment.

**Q: Where can I report bugs or suggest features?**  
**A:** Please open an issue on the official GitHub repository:  
[https://github.com/KalyanKS-NLP/ettin-pii/issues](https://github.com/KalyanKS-NLP/ettin-pii/issues)

