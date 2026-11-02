# Production-Ready PII Detection Toolkit: `ettin-pii`

A complete, beginner-to-advanced guide to developing a production-ready Python PII detection library using **`uv`** in **VS Code**, powered by the **Ettin Nemotron PII** model family by Kalyan KS.

---

## 1. Overview & Supported Model Family

The library provides built-in support for three specialized model sizes fine-tuned on NVIDIA's **Nemotron-PII** dataset, detecting **50+ Personally Identifiable Information (PII) entity types** (names, emails, phones, SSNs, credit cards, locations, IP addresses, credentials) across healthcare, finance, legal, and cyber domains:

| Model Alias | Hugging Face Repository | Parameter Size | Best For |
| :--- | :--- | :--- | :--- |
| **`"small"`** *(Default)* | [`kalyan-ks/ettin-68m-nemotron-pii`](https://huggingface.co/kalyan-ks/ettin-68m-nemotron-pii) | ~68.5M | Maximum accuracy (~96.27% F1), server workloads, audit pipelines |
| **`"tiny"`** | [`kalyan-ks/ettin-32m-nemotron-pii`](https://huggingface.co/kalyan-ks/ettin-32m-nemotron-pii) | ~32M | Balanced speed and accuracy for real-time CPU processing |
| **`"nano"`** | [`kalyan-ks/ettin-17m-nemotron-pii`](https://huggingface.co/kalyan-ks/ettin-17m-nemotron-pii) | ~17.5M | Ultra-low latency, serverless functions (AWS Lambda), edge devices |

> **Note:** The user can strictly select among these three official models (`"nano"`, `"tiny"`, `"small"`). Invalid model names will raise a clear validation error.

* **Library Scope (Features 1–5 & 7):**
  1. **Structured Result Objects:** `Entity`, `DetectionResult`, and `BatchDetectionResult` dataclasses with export and statistics support.
  2. **Multi-Strategy Redaction Engine:** `replace` (`<EMAIL>`), `mask` (`full`, `alternate`, `first_only`), `fake` (format-preserving synthetic scramble), and `custom` mapping.
  3. **High-Volume & Batch Processing:** Unified `detect()` method returning `DetectionResult` for single strings and `BatchDetectionResult` for batches.
  4. **Summary Statistics & Metrics:** `result.statistics` reporting entity counts, diversity, and text density (available on both single and batch results).
  5. **Multi-Format Export Handlers:** Native exports to JSON, CSV, dictionary, and Pandas DataFrames (`.to_dataframe()`) for both single and batch results.
  7. **Command Line Interface (CLI):** Ready-to-use `ettin-pii` CLI for terminal detection, redaction, and auditing.

---

## 2. Directory Architecture

```
ettin-pii/
├── pyproject.toml              # Project metadata, dependencies & CLI entry point
├── README.md                   # Documentation for library users
├── .python-version             # Python version pinned by uv
├── src/
│   └── ettin_pii/              # Main library package
│       ├── __init__.py         # Public exports (PIIDetector, Entity, DetectionResult, BatchDetectionResult, Redactor)
│       ├── models.py           # Feature 1 & 4: Entity, DetectionResult, and BatchDetectionResult
│       ├── redactor.py         # Feature 2: Multi-strategy redaction engine
│       ├── detector.py         # Feature 3: PIIDetector (unified detect for single & batch)
│       ├── cli.py              # Feature 7: ettin-pii CLI commands
│       └── output/             # Feature 5: Single & Batch Export handlers
│           ├── __init__.py
│           └── exporters.py    # JSON, CSV, DataFrame export logic
├── tests/
│   └── test_detector.py        # Automated test suite (models, redactor, detector)
└── example.py                  # End-to-end quickstart script
```

---

## Step 1: Install `uv` and Prepare VS Code

### 1. Install `uv` (Windows PowerShell)
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

Verify installation:
```powershell
uv --version
```

### 2. Open Project in VS Code
1. Open VS Code.
2. Select **File > Open Folder...** and choose your project directory:
   `E:\Kalyan_KS\LLM Projects\PII Detection Library`
3. Open the integrated terminal (`Ctrl + ` `~` or **Terminal > New Terminal**).

---

## Step 2: Initialize Project with `uv`

Scaffold a standard `src/` library package:

```powershell
uv init --lib
```

> **What this does:**
> - Creates `pyproject.toml` with standard PEP 621 packaging metadata.
> - Creates a `src/` directory for your library code.
> - Creates a `.python-version` file pinning the Python version.

### Do I need to explicitly run `uv venv`?

**No, you do NOT need to run `uv venv`.**

`uv` is designed to be completely **automatic**:
1. When you run `uv init --lib`, it scaffolds the project files (`pyproject.toml`, `src/`, `.python-version`).
2. As soon as you run **Step 3 (`uv add transformers torch`)**, `uv` automatically looks for a virtual environment.
3. If `.venv` doesn't exist yet, **`uv` creates `.venv` for you on the spot** and installs the packages into it.
4. When you run **`uv run python example.py`** or **`uv run pytest`**, `uv` automatically runs your code inside that `.venv` without you ever having to manually activate it!

**When would anyone run `uv venv`?**
The only reason someone would run `uv venv` manually is if they want to create an empty virtual environment to manually activate it in their terminal (e.g., `.\.venv\Scripts\activate`) or point an external IDE tool to it before adding any dependencies. For our workflow, `uv add` handles everything automatically.

**Summary:**
* `uv init --lib` $\rightarrow$ Creates project structure.
* `uv add transformers torch` $\rightarrow$ **Automatically creates `.venv`** and installs libraries.
* `uv run python example.py` $\rightarrow$ **Automatically executes** inside `.venv`.

---

## Step 3: Add Dependencies

Install runtime dependencies (`transformers` and `torch`), optional data science support (`pandas`), and test runner (`pytest`):

```powershell
# Core model & pipeline dependencies
uv add transformers torch

# Optional data export support
uv add pandas

# Developer test dependencies
uv add --dev pytest
```

---

## Step 4: Configure `pyproject.toml` & CLI Entry Point

Update `pyproject.toml` in the project root to define metadata and register the **`ettin-pii`** CLI command:

```toml
[project]
name = "ettin-pii"
version = "0.1.0"
description = "Production-ready PII detection and redaction toolkit powered by the Ettin Nemotron PII model family"
readme = "README.md"
authors = [{ name = "Kalyan KS" }]
requires-python = ">=3.10"
dependencies = [
    "torch>=2.0.0",
    "transformers>=4.40.0",
    "pandas>=2.0.0",
]

[project.urls]
Homepage = "https://github.com/kalyan-ks/ettin-pii"
Repository = "https://github.com/kalyan-ks/ettin-pii"
Issues = "https://github.com/kalyan-ks/ettin-pii/issues"

[project.scripts]
ettin-pii = "ettin_pii.cli:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[dependency-groups]
dev = [
    "pytest>=8.0.0",
]
```

### Understanding the `pyproject.toml` Sections:

1. **`[project]` — The Library's ID Card & Must-Haves**
   * **What it does:** Tells Python and PyPI who you are, what your package is called, its version, and what external packages it **must** install to work.
   * **In simple terms:** When someone runs `pip install ettin-pii`, Python reads this section to know it needs to download `torch`, `transformers`, and `pandas` so your library can actually run.

2. **`[project.urls]` — Project Web Links on PyPI**
   * **What it does:** Adds clickable links directly on your official PyPI page for your GitHub repository, bug tracker, and homepage.

3. **`[project.scripts]` — The Terminal Shortcut (CLI)**
   * **What it does:** Creates a command-line shortcut.
   * **In simple terms:** Instead of typing `python -m ettin_pii.cli`, users can just type `ettin-pii` directly into their terminal. It maps the word `ettin-pii` to the `main()` function inside `src/ettin_pii/cli.py`.

4. **`[build-system]` — The Factory Machine (Packaging Tool)**
   * **What it does:** Specifies the tool that builds your raw Python files into a distributable package (`.whl` or `.tar.gz`).
   * **In simple terms:** Here, `hatchling` is the factory worker that packages your code neatly into a box so you can upload it to PyPI and others can download it.

5. **`[dependency-groups]` — Tools Just for You (The Developer)**
   * **What it does:** Lists packages needed **only** during development and testing, not by regular users.
   * **In simple terms:** Regular users only need your library to detect PII; they don't need `pytest`. This section tells `uv` to install `pytest` on **your** computer so you can run tests without forcing regular users to download it.

---

## Step 5: Implement Library Components

### 1. Feature 1 & 4: Structured Models (`src/ettin_pii/models.py`)

Defines `Entity`, `DetectionResult`, and `BatchDetectionResult`, including summary statistics and export methods.

#### Understanding Key Python Concepts (`@dataclass`, `@property`, `TYPE_CHECKING`, `__future__`, and Dunder Methods) in Simple English:

1. **What is `@dataclass`? (The Boilerplate Eliminator)**
   In standard Python, whenever you create a class to store data, you are forced to write repetitive code:
   ```python
   # ❌ The manual, boring way without @dataclass:
   class Entity:
       def __init__(self, text, label, score, start, end):
           self.text = text
           self.label = label
           self.score = score
           self.start = start
           self.end = end
   ```
   * **What `@dataclass` does:** It automatically writes `__init__()`, readable printing (`__repr__`), and comparisons (`==`) for you behind the scenes. You just list the field names and their types!
   * **What `(frozen=True)` means:** It makes the object **read-only (immutable)**. Once an entity is created, no one can accidentally modify it (e.g., trying `entity.score = 0.1` will raise an error). This is great for security and audit logs.

2. **What is `@property`? (The Smart Calculated Variable)**
   `@property` turns a method (function) into an **attribute that you can access without parentheses `()`**.
   * **In the code:**
     ```python
     @property
     def length(self) -> int:
         return self.end - self.start
     ```
   * **Without `@property`:** You would have to call it like a function with brackets: `entity.length()`.
   * **With `@property`:** You access it cleanly just like a normal variable: `entity.length`.
   * **Why use it here?** Instead of wasting memory storing a separate `length` number in RAM, `@property` **calculates it dynamically on the fly** (`end - start`) only when you ask for it.

3. **What is `if TYPE_CHECKING:`? (The Invisible Ink for Imports)**
   > **`if TYPE_CHECKING:` is like "invisible ink": VS Code can see it to give you autocomplete, but Python ignores it completely when running the code.**
   
   * **`pandas` is heavy and slow:** If you write `import pandas` normally, Python has to load it every time you start your library, making it slow.
   * **What if the user doesn't have `pandas` installed?** If you write `import pandas` normally, your library will **crash immediately** with an error: *"No module named pandas"*.
   * **With `if TYPE_CHECKING:`:**
     * **VS Code** sees it $\rightarrow$ allows you to write `-> pd.DataFrame` with helpful autocomplete.
     * **Python running your code** skips it $\rightarrow$ the library starts instantly and **never crashes**, even if `pandas` is not installed!

4. **What does `from __future__ import annotations` do?**
   In one simple sentence:
   > **It tells Python: "Treat all type hints as plain text comments instead of trying to execute them immediately."**

   **How it makes `if TYPE_CHECKING:` actually work (Our exact case):**
   Remember this code in `models.py`:
   ```python
   if TYPE_CHECKING:
       import pandas as pd   # <-- NOT imported when Python runs!

   class DetectionResult:
       def to_dataframe(self) -> pd.DataFrame:
           ...
   ```
   * ❌ **Without `from __future__ import annotations`:** When Python runs this file, `pd` is not imported. When it reads `-> pd.DataFrame:`, Python panics and crashes: `NameError: name 'pd' is not defined`!
   * ✅ **With `from __future__ import annotations`:** Python treats `pd.DataFrame` as harmless plain text while running. It doesn't look for `pd`, so your code runs with zero errors!

5. **What are Double-Underscore Functions (`__len__`, `__getitem__`, `__iter__`)? (Dunder / Magic Methods)**
   In Python, functions with double underscores at the start and end (like `__len__`) are called **"Dunder Methods"** (short for **D**ouble **Under**score) or **Magic Methods**.

   * **Why the double underscores?**
     Python's way of saying:
     > *"This is **not** a regular function that users call by name (nobody writes `batch.__len__()`). Instead, this is a **special hook** that connects your custom class to Python's built-in syntax like `len()`, `for` loops, and square brackets `[]`."*

   * **What each one connects to in plain English:**
     * `def __len__(self)` $\rightarrow$ Powers `len(batch)`: When a user writes `len(batch)`, Python secretly calls `batch.__len__()` behind the scenes to give the count!
     * `def __getitem__(self, index)` $\rightarrow$ Powers square brackets `batch[0]`: When a user writes `batch[0]`, Python secretly calls `batch.__getitem__(0)` so your object acts just like a real Python list!
     * `def __iter__(self)` $\rightarrow$ Powers `for` loops: When a user writes `for r in batch:`, Python secretly calls `batch.__iter__()` so you can loop over the results smoothly!

   * **The Big Benefit:**
     These 3 small magic methods make `BatchDetectionResult` **behave exactly like a native Python list** (`len()`, `batch[0]`, `for r in batch:` all work!), while **still** having custom tools like `batch.to_csv()` and `batch.to_dataframe()`!

#### Code Implementation:

```python
"""
Models and Data Structures for ettin-pii.
"""
from __future__ import annotations
import json
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Iterator, TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd


@dataclass(frozen=True)
class Entity:
    """Represents a single detected PII entity."""
    text: str
    label: str
    score: float
    start: int
    end: int

    @property
    def length(self) -> int:
        """Character length of the entity span."""
        return self.end - self.start

    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to standard Python dictionary."""
        return {
            "text": self.text,
            "label": self.label,
            "score": round(self.score, 4),
            "start": self.start,
            "end": self.end,
            "length": self.length,
        }

    def to_json(self) -> str:
        """Serialize entity to JSON string."""
        return json.dumps(self.to_dict())


@dataclass
class DetectionResult:
    """Represents the complete detection output for a piece of text."""
    text: str
    entities: List[Entity] = field(default_factory=list)

    @property
    def num_entities(self) -> int:
        """Total number of entities detected."""
        return len(self.entities)

    @property
    def has_pii(self) -> bool:
        """True if at least one PII entity was detected."""
        return len(self.entities) > 0

    @property
    def redacted_text(self) -> str:
        """Convenience property: returns text redacted with default label strategy."""
        return self.redact(strategy="replace")

    @property
    def statistics(self) -> Dict[str, Any]:
        """
        Feature 4: Computes quantitative summary metrics of detected PII.
        """
        counts: Dict[str, int] = {}
        total_pii_chars = 0
        total_score = 0.0

        for ent in self.entities:
            counts[ent.label] = counts.get(ent.label, 0) + 1
            total_pii_chars += ent.length
            total_score += ent.score

        text_len = len(self.text)
        density = round(total_pii_chars / text_len, 4) if text_len > 0 else 0.0
        avg_confidence = round(total_score / len(self.entities), 4) if self.entities else 0.0

        return {
            "total_entities": self.num_entities,
            "unique_entity_types": len(counts),
            "entity_counts": counts,
            "density": density,
            "average_confidence": avg_confidence,
        }

    def redact(self, strategy: str = "replace", **kwargs) -> str:
        """
        Feature 2: Redacts detected sensitive spans using the Redactor engine.
        """
        from .redactor import Redactor
        return Redactor.apply(self.text, self.entities, strategy=strategy, **kwargs)

    # Feature 5: Export Handlers
    def to_dict(self) -> Dict[str, Any]:
        """Convert full result to serializable dictionary."""
        return {
            "text": self.text,
            "entities": [e.to_dict() for e in self.entities],
            "statistics": self.statistics,
        }

    def to_json(self, filepath: Optional[str] = None, indent: int = 2) -> str:
        """Export result to JSON string or write directly to filepath."""
        from .output.exporters import export_to_json
        return export_to_json(self, filepath=filepath, indent=indent)

    def to_csv(self, filepath: str) -> None:
        """Export detected entities to a CSV spreadsheet."""
        from .output.exporters import export_to_csv
        export_to_csv(self, filepath=filepath)

    def to_dataframe(self) -> pd.DataFrame:
        """Convert detected entities to a Pandas DataFrame."""
        from .output.exporters import export_to_dataframe
        return export_to_dataframe(self)


@dataclass
class BatchDetectionResult:
    """
    Represents detection results for a batch of texts.
    Acts as an iterable container with batch-level export and statistics capabilities.
    """
    results: List[DetectionResult] = field(default_factory=list)

    def __len__(self) -> int:
        return len(self.results)

    def __iter__(self) -> Iterator[DetectionResult]:
        return iter(self.results)

    def __getitem__(self, index: int) -> DetectionResult:
        return self.results[index]

    @property
    def redacted_texts(self) -> List[str]:
        """List of redacted text strings across the entire batch."""
        return [r.redacted_text for r in self.results]

    def redact(self, strategy: str = "replace", **kwargs) -> List[str]:
        """Redact all texts in the batch using the specified strategy."""
        return [r.redact(strategy=strategy, **kwargs) for r in self.results]

    @property
    def total_entities(self) -> int:
        """Total entities detected across all texts in the batch."""
        return sum(r.num_entities for r in self.results)

    @property
    def statistics(self) -> Dict[str, Any]:
        """Aggregated summary statistics for the entire batch."""
        total_texts = len(self.results)
        texts_with_pii = sum(1 for r in self.results if r.has_pii)
        combined_counts: Dict[str, int] = {}
        total_entities = 0

        for r in self.results:
            for ent in r.entities:
                combined_counts[ent.label] = combined_counts.get(ent.label, 0) + 1
                total_entities += 1

        return {
            "total_texts": total_texts,
            "texts_with_pii": texts_with_pii,
            "total_entities": total_entities,
            "unique_entity_types": len(combined_counts),
            "entity_counts": combined_counts,
        }

    def to_dict(self) -> Dict[str, Any]:
        """Serialize entire batch to dictionary."""
        return {
            "statistics": self.statistics,
            "results": [
                {
                    "text_index": i,
                    **r.to_dict()
                }
                for i, r in enumerate(self.results)
            ],
        }

    def to_json(self, filepath: Optional[str] = None, indent: int = 2) -> str:
        """Export batch results to JSON string or save to file."""
        from .output.exporters import export_batch_to_json
        return export_batch_to_json(self, filepath=filepath, indent=indent)

    def to_csv(self, filepath: str) -> None:
        """Export all detected entities across the batch to a combined CSV."""
        from .output.exporters import export_batch_to_csv
        export_batch_to_csv(self, filepath=filepath)

    def to_dataframe(self) -> pd.DataFrame:
        """Convert all detected entities across the batch into a combined Pandas DataFrame."""
        from .output.exporters import export_batch_to_dataframe
        return export_batch_to_dataframe(self)
```

---

### 2. Feature 2: Multi-Strategy Redaction Engine (`src/ettin_pii/redactor.py`)

Provides 4 distinct anonymization strategies, including 3 masking sub-modes, format-preserving synthetic faking, and customizable dictionary mapping:

#### How the `"custom"` Redaction Option Works:
When `strategy="custom"` is chosen, the `Redactor` follows 3 simple steps:
1. **Detects the Entity:** Finds the sensitive span and its label (e.g., `label="email"`).
2. **Looks up your Dictionary:** It checks your `mapping` dictionary to see if you provided a custom rule for `"email"`.
3. **Applies the Replacement (with a Safe Fallback):**
   * If the label is in your dictionary, it uses your custom string.
   * **Safety Fallback:** If the model detects an entity you forgot to include in your dictionary (e.g., `credit_card`), it automatically falls back to `<CREDIT_CARD>` so no private data accidentally leaks.

#### Code Implementation:

```python
"""
Multi-Strategy Redaction Engine for ettin-pii.
"""
import random
import string
from typing import List, Dict, Optional
from .models import Entity


class Redactor:
    """
    Applies configurable redaction strategies to text using detected entities.
    """

    @staticmethod
    def _mask_span(span_text: str, mask_char: str = "*", mask_mode: str = "full") -> str:
        """
        Helper for masking entity spans.
        - 'full': Masks every character in the span (e.g. '****').
        - 'alternate': Masks every second character (e.g. 'a*e*.*u*p*y').
        - 'first_only': Keeps the first character of each word, masks the rest (e.g. 'A*** M*****').
        """
        if not span_text:
            return ""

        if mask_mode == "full":
            return mask_char * len(span_text)

        elif mask_mode == "alternate":
            chars = []
            for i, ch in enumerate(span_text):
                if ch.isspace() or ch in "@.-_/+":
                    chars.append(ch)
                elif i % 2 == 1:
                    chars.append(mask_char)
                else:
                    chars.append(ch)
            return "".join(chars)

        elif mask_mode == "first_only":
            words = span_text.split(" ")
            masked_words = []
            for word in words:
                if len(word) <= 1:
                    masked_words.append(word)
                else:
                    masked_words.append(word[0] + (mask_char * (len(word) - 1)))
            return " ".join(masked_words)

        else:
            raise ValueError(
                f"Unknown mask_mode: '{mask_mode}'. Supported modes: 'full', 'alternate', 'first_only'."
            )

    @staticmethod
    def _fake_span(span_text: str) -> str:
        """
        Replaces letters and digits with random ones of the same type,
        preserving case, punctuation, spaces, and symbols (@, ., -, etc.).
        """
        scrambled = []
        for ch in span_text:
            if ch.islower():
                scrambled.append(random.choice(string.ascii_lowercase))
            elif ch.isupper():
                scrambled.append(random.choice(string.ascii_uppercase))
            elif ch.isdigit():
                scrambled.append(random.choice(string.digits))
            else:
                scrambled.append(ch)
        return "".join(scrambled)

    @staticmethod
    def apply(
        text: str,
        entities: List[Entity],
        strategy: str = "replace",
        mask_char: str = "*",
        mask_mode: str = "full",
        mapping: Optional[Dict[str, str]] = None,
    ) -> str:
        """
        Redact sensitive information from text.

        :param text: Original raw text.
        :param entities: List of detected Entity objects.
        :param strategy: 'replace', 'mask', 'fake', or 'custom'.
        :param mask_char: Character to use when strategy='mask' (default: '*').
        :param mask_mode: Sub-mode for 'mask': 'full', 'alternate', or 'first_only'.
        :param mapping: Dictionary mapping entity labels to custom placeholders (for 'custom').
        :return: Sanitized string.
        """
        if not text or not entities:
            return text

        # Sort entities in reverse order by start index so replacements
        # do not alter character indices of preceding entities
        sorted_entities = sorted(entities, key=lambda x: x.start, reverse=True)
        sanitized = text

        for ent in sorted_entities:
            start, end, label, span_text = ent.start, ent.end, ent.label, ent.text

            if strategy == "replace":
                replacement = f"<{label.upper()}>"

            elif strategy == "mask":
                replacement = Redactor._mask_span(span_text, mask_char=mask_char, mask_mode=mask_mode)

            elif strategy == "fake":
                replacement = Redactor._fake_span(span_text)

            elif strategy == "custom":
                replacement = mapping.get(label, f"<{label.upper()}>") if mapping else f"<{label.upper()}>"

            else:
                raise ValueError(
                    f"Unknown strategy: '{strategy}'. Supported: 'replace', 'mask', 'fake', 'custom'."
                )

            sanitized = sanitized[:start] + replacement + sanitized[end:]

        return sanitized
```

---

### 3. Feature 3: Detection Pipeline (`src/ettin_pii/detector.py`)

Handles single-string detection, mini-batch GPU/CPU inference, choice of model (`small`, `tiny`, `nano`), and official entity post-processing (adjacent span merging and whitespace offset re-alignment).

#### Why is `_format_pii_entities()` a `@classmethod`?

`_format_pii_entities()` does **not** need the loaded PyTorch model or GPU instance (`self`), but it **does** need to call another helper method on the class (`cls._clean_entity`).

1. **It Doesn't Touch Model State (`self`):**
   A normal method uses `self` because it accesses `self.pipeline` or `self.confidence_threshold`. `_format_pii_entities` is pure text/dictionary manipulation—it only processes the inputs passed into it (`entities` and `original_text`). It doesn't need the heavy Hugging Face model loaded into RAM to do its work.

2. **It Calls `cls._clean_entity(...)`:**
   Because it is a `@classmethod`, Python passes `cls` (the class itself) as the first argument. This allows `_format_pii_entities` to cleanly call the sibling helper `_clean_entity` without having to hardcode `PIIDetector._clean_entity(...)`.

3. **It Allows Fast Testing & Subclassing:**
   * **For Testing:** You can test the formatting logic in a unit test **instantly** without waiting for the 68M model to download or load into memory (`PIIDetector._format_pii_entities(raw_data, text)`).
   * **For Subclassing:** If an advanced developer subclasses `PIIDetector` and customizes `_clean_entity`, `cls._clean_entity` will automatically use *their* version.

| Method Type | First Parameter | When to use? |
| :--- | :--- | :--- |
| **Regular (`def method(self)`)** | `self` (the instance) | When you need the loaded pipeline or model state (`self.pipeline`). |
| **`@classmethod` (`def method(cls)`)** | `cls` (the class) | When you don't need `self`, but you need to call other class methods (`cls._clean_entity`) or support subclass overrides. |
| **`@staticmethod` (`def method()`)** | *None* | For completely standalone utilities that don't reference any other methods in the class. |

#### Code Implementation:

```python
"""
Core PIIDetector class for ettin-pii.
"""
from typing import List, Optional, Literal, Union, overload
from transformers import pipeline
from .models import Entity, DetectionResult, BatchDetectionResult

# Supported Ettin Nemotron PII model family
MODEL_REGISTRY = {
    "nano": "kalyan-ks/ettin-17m-nemotron-pii",
    "tiny": "kalyan-ks/ettin-32m-nemotron-pii",
    "small": "kalyan-ks/ettin-68m-nemotron-pii",
}
DEFAULT_MODEL = "small"


class PIIDetector:
    """
    Production-ready PII detector powered by the Ettin Nemotron PII model family.
    """

    def __init__(
        self,
        model: Literal["nano", "tiny", "small"] = "small",
        device: Optional[str] = None,
        batch_size: int = 16,
        confidence_threshold: float = 0.50,
    ):
        """
        Initialize the detector pipeline.

        :param model: Choose model size: 'nano' (17M), 'tiny' (32M), or 'small' (68M, default).
        :param device: 'cpu', 'cuda', or None (auto-detect).
        :param batch_size: Default batch size for batch processing.
        :param confidence_threshold: Minimum confidence score (0.0 to 1.0).
        """
        model_key = model.lower()
        if model_key not in MODEL_REGISTRY:
            raise ValueError(
                f"Invalid model '{model}'. Supported models: {list(MODEL_REGISTRY.keys())} ('nano', 'tiny', 'small')."
            )

        self.model_alias = model_key
        self.model_name = MODEL_REGISTRY[model_key]
        self.batch_size = batch_size
        self.confidence_threshold = confidence_threshold

        device_id = -1
        if device == "cuda":
            device_id = 0
        elif device is None:
            import torch
            device_id = 0 if torch.cuda.is_available() else -1

        # Use token-classification with aggregation_strategy='simple'
        # to automatically stitch subwords into complete entity spans
        self.pipeline = pipeline(
            task="token-classification",
            model=self.model_name,
            aggregation_strategy="simple",
            device=device_id,
        )

    @staticmethod
    def _clean_entity(ent: dict) -> dict:
        """Strip surrounding spaces and adjust character offsets accordingly."""
        raw_text = ent["text"]
        stripped_text = raw_text.strip()
        leading_spaces = len(raw_text) - len(raw_text.lstrip())

        start = ent["start"] + leading_spaces
        end = start + len(stripped_text)

        return {
            "start": start,
            "end": end,
            "text": stripped_text,
            "label": ent["label"],
            "score": ent.get("score", 1.0),
        }

    @classmethod
    def _format_pii_entities(cls, entities: list, original_text: str) -> list:
        """
        Post-process raw token-classification entities (from official model card):
        - Merges adjacent entities sharing the same label (e.g., 'Kalyan' + 'KS' -> 'Kalyan KS').
        - Re-aligns exact start/end character offsets with the original text.
        - Strips whitespace artifacts while preserving exact boundaries.
        """
        if not entities:
            return []

        # Sort entities by start offset
        entities = sorted(entities, key=lambda x: x["start"])

        current_entity = {
            "start": entities[0]["start"],
            "end": entities[0]["end"],
            "label": entities[0].get("entity_group", entities[0].get("entity", "PII")),
            "text": entities[0].get("word", ""),
            "score": float(entities[0].get("score", 1.0)),
        }

        merged_entities = []

        for next_ent in entities[1:]:
            next_label = next_ent.get("entity_group", next_ent.get("entity", "PII"))
            is_same_label = next_label == current_entity["label"]
            is_adjacent = next_ent["start"] <= current_entity["end"] + 1

            if is_same_label and is_adjacent:
                current_entity["end"] = max(current_entity["end"], next_ent["end"])
                current_entity["text"] = original_text[current_entity["start"]:current_entity["end"]]
                current_entity["score"] = max(current_entity["score"], float(next_ent.get("score", 1.0)))
            else:
                merged_entities.append(cls._clean_entity(current_entity))
                current_entity = {
                    "start": next_ent["start"],
                    "end": next_ent["end"],
                    "label": next_label,
                    "text": next_ent.get("word", ""),
                    "score": float(next_ent.get("score", 1.0)),
                }

        merged_entities.append(cls._clean_entity(current_entity))
        return merged_entities

    def _parse_entities(self, raw_entities: list, original_text: str) -> List[Entity]:
        """Format, filter, and convert raw pipeline outputs into Entity objects."""
        formatted = self._format_pii_entities(raw_entities, original_text)
        parsed = []
        for item in formatted:
            score = float(item["score"])
            if score >= self.confidence_threshold:
                parsed.append(
                    Entity(
                        text=item["text"],
                        label=item["label"],
                        score=round(score, 4),
                        start=item["start"],
                        end=item["end"],
                    )
                )
        return parsed

    @overload
    def detect(self, text_or_texts: str, batch_size: Optional[int] = None) -> DetectionResult:
        ...

    @overload
    def detect(self, text_or_texts: List[str], batch_size: Optional[int] = None) -> BatchDetectionResult:
        ...

    def detect(
        self,
        text_or_texts: Union[str, List[str]],
        batch_size: Optional[int] = None,
    ) -> Union[DetectionResult, BatchDetectionResult]:
        """
        Detect PII in a single text string or across a batch (list) of strings.

        :param text_or_texts: Single input string or list of strings.
        :param batch_size: Batch size for inference when passing a list (defaults to self.batch_size).
        :return: DetectionResult for a single string, or BatchDetectionResult for a list.
        """
        # Case 1: Single string input
        if isinstance(text_or_texts, str):
            if not text_or_texts or not text_or_texts.strip():
                return DetectionResult(text=text_or_texts, entities=[])

            raw_outputs = self.pipeline(text_or_texts)
            entities = self._parse_entities(raw_outputs, text_or_texts)
            return DetectionResult(text=text_or_texts, entities=entities)

        # Case 2: Batch (list of strings) input
        if not text_or_texts:
            return BatchDetectionResult(results=[])

        bs = batch_size or self.batch_size
        raw_batch_outputs = self.pipeline(text_or_texts, batch_size=bs)

        results = []
        for text, raw_entities in zip(text_or_texts, raw_batch_outputs):
            entities = self._parse_entities(raw_entities, text)
            results.append(DetectionResult(text=text, entities=entities))

        return BatchDetectionResult(results=results)
```

---

### 4. Feature 5: Export Handlers (`src/ettin_pii/output/exporters.py`)

Handles JSON, CSV, and Pandas DataFrame exports for both single and batch results:

```python
"""
Multi-Format Export Logic for DetectionResult and BatchDetectionResult.
"""
from __future__ import annotations
import csv
import json
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd
    from ..models import DetectionResult, BatchDetectionResult


# --- Single Result Exporters ---

def export_to_json(result: DetectionResult, filepath: Optional[str] = None, indent: int = 2) -> str:
    """Serialize DetectionResult to JSON string or write to disk."""
    data = result.to_dict()
    json_str = json.dumps(data, indent=indent)
    if filepath:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(json_str)
    return json_str


def export_to_csv(result: DetectionResult, filepath: str) -> None:
    """Write detected entities to a CSV spreadsheet."""
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["label", "text", "score", "start", "end", "length"])
        for entity in result.entities:
            writer.writerow([
                entity.label,
                entity.text,
                entity.score,
                entity.start,
                entity.end,
                entity.length,
            ])


def export_to_dataframe(result: DetectionResult) -> pd.DataFrame:
    """Convert detected entities to a Pandas DataFrame."""
    try:
        import pandas as pd
    except ImportError:
        raise ImportError("Pandas is required for DataFrame export. Install it with: uv add pandas")

    records = [entity.to_dict() for entity in result.entities]
    return pd.DataFrame(records)


# --- Batch Result Exporters ---

def export_batch_to_json(batch: BatchDetectionResult, filepath: Optional[str] = None, indent: int = 2) -> str:
    """Serialize BatchDetectionResult to JSON string or write to disk."""
    data = batch.to_dict()
    json_str = json.dumps(data, indent=indent)
    if filepath:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(json_str)
    return json_str


def export_batch_to_csv(batch: BatchDetectionResult, filepath: str) -> None:
    """Write all detected entities across a batch to a combined CSV with text_index and source_text."""
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["text_index", "label", "text", "score", "start", "end", "length", "source_text"])
        for idx, result in enumerate(batch.results):
            for entity in result.entities:
                writer.writerow([
                    idx,
                    entity.label,
                    entity.text,
                    entity.score,
                    entity.start,
                    entity.end,
                    entity.length,
                    result.text,
                ])


def export_batch_to_dataframe(batch: BatchDetectionResult) -> pd.DataFrame:
    """Convert all detected entities across a batch into a combined Pandas DataFrame."""
    try:
        import pandas as pd
    except ImportError:
        raise ImportError("Pandas is required for DataFrame export. Install it with: uv add pandas")

    records = []
    for idx, result in enumerate(batch.results):
        for entity in result.entities:
            records.append({
                "text_index": idx,
                "label": entity.label,
                "text": entity.text,
                "score": entity.score,
                "start": entity.start,
                "end": entity.end,
                "length": entity.length,
                "source_text": result.text,
            })
    return pd.DataFrame(records)
```

---

### 5. Package Exports (`src/ettin_pii/__init__.py`)

#### What is `__init__.py`? (The Simple Analogy)

Think of a folder in your project as a building, and `__init__.py` as the reception desk at the front door.

Without a reception desk, a visitor has to wander down the hallway, find the right room number, and open the exact desk drawer:

```python
# ❌ Without __init__.py: Ugly and annoying to remember
from ettin_pii.detector import PIIDetector
from ettin_pii.models import DetectionResult, Entity, BatchDetectionResult
from ettin_pii.redactor import Redactor
```

With `__init__.py`, the reception desk brings everything to the front entrance for you:

```python
# ✅ With __init__.py: Clean, elegant, and professional
from ettin_pii import PIIDetector, DetectionResult
```

#### Code Implementation:

Exposes a clean top-level API:

```python
"""
ettin-pii: Production-Ready PII Detection and Redaction Toolkit
"""
from .detector import PIIDetector
from .models import Entity, DetectionResult, BatchDetectionResult
from .redactor import Redactor

__version__ = "0.1.0"
__all__ = ["PIIDetector", "Entity", "DetectionResult", "BatchDetectionResult", "Redactor"]
```

#### What does `__all__` represent?

In simple terms, `__all__` is the VIP Guest List (or Public Menu) of your library.

It tells Python:

> "Out of everything inside this package, only these 5 items are official, public tools meant for users to see and use."

**What does it actually do? (The 2 Big Roles)**

1. **It Protects Against `from ettin_pii import *` (Wildcard Imports)**

   If a user writes:

   ```python
   from ettin_pii import *
   ```

   Python checks `__all__`. It will only import `PIIDetector`, `Entity`, `DetectionResult`, `BatchDetectionResult`, and `Redactor`.

   Any internal helper variables, private functions, or imported modules (like `json`, `csv`, or `sys`) are hidden and won't clutter the user's script.

2. **It Tells VS Code and Autocomplete What to Show**

   When someone uses your library in VS Code and types:

   ```python
   import ettin_pii
   ettin_pii.   # <-- Autocomplete popup appears
   ```

   VS Code looks at `__all__` and only suggests those 5 approved public classes. It keeps the autocomplete suggestions clean, uncluttered, and professional.

---

### 6. Feature 7: Command Line Interface (`src/ettin_pii/cli.py`)

#### Understanding CLI Flags (`--output` vs `-o`):

In that line, `-o` is the short flag (shortcut) for `--output`. The letter **`o`** simply stands for **Output**.

**Why do CLI tools provide both `--output` and `-o`?**

It gives users two ways to write the same command:
* **The Long Form (`--output`):** Great for scripts and documentation because it is clear and easy to read:
  ```bash
  ettin-pii redact input.txt --output clean.txt
  ```
* **The Short Form (`-o`):** Great when you are quickly typing in the terminal and don't want to type out the full word `--output`:
  ```bash
  ettin-pii redact input.txt -o clean.txt
  ```

#### How `cli.py` Works (The 5 Simple Steps):

1. **Setting up Subcommands (`argparse`):**
   Creates 3 specialized subcommands:
   * **`detect`**: Scans text or a file and displays detected entities (or exports to JSON).
   * **`redact`**: Sanitizes text using `replace`, `mask`, or `fake` and prints/saves the cleaned output.
   * **`stats`**: Generates a privacy audit report with entity counts and text density.

2. **Configuring Options and Flags:**
   * `--model`: Lets users switch between `nano`, `tiny`, and `small` (defaults to `small`).
   * `--threshold`: Sets minimum confidence score (e.g., `--threshold 0.7`).
   * `--batch` / `-b`: Processes multi-line files or text line-by-line as a batch of independent records.
   * `--verbose` / `-v`: Shows detailed lists of extracted entities with confidence scores and offsets (for `stats`).
   * `--strategy` & `--mask-mode`: Choose how to mask (for `redact`).
   * `-o` / `--output`: Optional file path to save results instead of just printing to screen.

3. **Smart Input Reading (Text vs. File):**
   * If the user passes a file name (e.g., `input.txt`), it automatically opens and reads the file.
   * If the user types raw text directly (e.g., `"Hello, my name is Alex"`), it detects it's not a file and processes the text directly.

4. **Running the Model:**
   Loads the requested Ettin model and runs `detector.detect(content)`.

5. **Handling Output:**
   * **`detect`:** Prints each entity's label, text, and score (or exports to JSON with `-o`).
   * **`redact`:** Redacts the text with the chosen strategy and prints/saves the output.
   * **`stats`:** Prints a clean summary table showing total entities, text density, and counts by label (and supports `-v` / `--verbose` to list extracted entities alongside metrics).

#### Code Implementation:

Implements the terminal command `ettin-pii`:

```python
"""
Command Line Interface for ettin-pii.
"""
import sys
import argparse
from .detector import PIIDetector
from .models import BatchDetectionResult


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="ettin-pii",
        description="Fast PII Detection and Redaction CLI powered by the Ettin Nemotron PII model family",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcommand: detect
    detect_parser = subparsers.add_parser("detect", help="Scan text or file for PII entities")
    detect_parser.add_argument("input", help="Raw text string or path to a text file")
    detect_parser.add_argument(
        "--model",
        choices=["nano", "tiny", "small"],
        default="small",
        help="PII model size: nano (17M), tiny (32M), or small (68M, default)",
    )
    detect_parser.add_argument("--threshold", type=float, default=0.5, help="Confidence threshold (0.0-1.0)")
    detect_parser.add_argument(
        "--batch",
        "-b",
        action="store_true",
        help="Process input line-by-line as a batch of independent records",
    )
    detect_parser.add_argument("--output", "-o", help="Optional JSON output filepath")

    # Subcommand: redact
    redact_parser = subparsers.add_parser("redact", help="Sanitize text or file")
    redact_parser.add_argument("input", help="Raw text string or path to a text file")
    redact_parser.add_argument(
        "--model",
        choices=["nano", "tiny", "small"],
        default="small",
        help="PII model size: nano (17M), tiny (32M), or small (68M, default)",
    )
    redact_parser.add_argument("--threshold", type=float, default=0.5, help="Confidence threshold (0.0-1.0)")
    redact_parser.add_argument(
        "--batch",
        "-b",
        action="store_true",
        help="Process input line-by-line as a batch of independent records",
    )
    redact_parser.add_argument(
        "--strategy",
        choices=["replace", "mask", "fake"],
        default="replace",
        help="Redaction strategy to apply",
    )
    redact_parser.add_argument("--mask-char", default="*", help="Masking character (default: *)")
    redact_parser.add_argument(
        "--mask-mode",
        choices=["full", "alternate", "first_only"],
        default="full",
        help="Masking style when strategy='mask' (default: full)",
    )
    redact_parser.add_argument("--output", "-o", help="Optional output filepath for sanitized text")

    # Subcommand: stats
    stats_parser = subparsers.add_parser("stats", help="Show summary PII statistics and density")
    stats_parser.add_argument("input", help="Raw text string or path to a text file")
    stats_parser.add_argument(
        "--model",
        choices=["nano", "tiny", "small"],
        default="small",
        help="PII model size: nano (17M), tiny (32M), or small (68M, default)",
    )
    stats_parser.add_argument("--threshold", type=float, default=0.5, help="Confidence threshold (0.0-1.0)")
    stats_parser.add_argument(
        "--batch",
        "-b",
        action="store_true",
        help="Process input line-by-line as a batch of independent records",
    )
    stats_parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Include detailed list of extracted entities with scores and offsets",
    )

    args = parser.parse_args()

    is_batch = getattr(args, "batch", False)

    # Read input from file if existing path, else treat as raw string
    try:
        with open(args.input, "r", encoding="utf-8") as f:
            if is_batch:
                content = [line.strip() for line in f if line.strip()]
            else:
                content = f.read()
    except (FileNotFoundError, OSError):
        if is_batch:
            content = [line.strip() for line in args.input.splitlines() if line.strip()]
        else:
            content = args.input

    detector = PIIDetector(
        model=args.model,
        confidence_threshold=getattr(args, "threshold", 0.5),
    )
    result = detector.detect(content)

    if args.command == "detect":
        if isinstance(result, BatchDetectionResult):
            if args.output:
                result.to_json(args.output)
                print(f"Batch entities exported to {args.output}")
            else:
                print(f"\nProcessed {len(result)} records (Total PII: {result.total_entities}):")
                for i, r in enumerate(result):
                    if r.has_pii:
                        print(f" [Record #{i+1}] '{r.text}'")
                        for ent in r.entities:
                            print(f"   - [{ent.label}] '{ent.text}' (Score: {ent.score:.2%}, Offsets: {ent.start}-{ent.end})")
        else:
            if args.output:
                result.to_json(args.output)
                print(f"Entities exported to {args.output}")
            else:
                print(f"\nFound {result.num_entities} PII entities:")
                for ent in result.entities:
                    print(f" - [{ent.label}] '{ent.text}' (Score: {ent.score:.2%}, Offsets: {ent.start}-{ent.end})")

    elif args.command == "redact":
        sanitized = result.redact(
            strategy=args.strategy,
            mask_char=args.mask_char,
            mask_mode=args.mask_mode,
        )
        if isinstance(result, BatchDetectionResult):
            if args.output:
                with open(args.output, "w", encoding="utf-8") as f:
                    f.write("\n".join(sanitized) + "\n")
                print(f"Sanitized {len(sanitized)} records saved to {args.output}")
            else:
                for line in sanitized:
                    print(line)
        else:
            if args.output:
                with open(args.output, "w", encoding="utf-8") as f:
                    f.write(sanitized)
                print(f"Sanitized text saved to {args.output}")
            else:
                print(sanitized)

    elif args.command == "stats":
        if isinstance(result, BatchDetectionResult):
            stats = result.statistics
            total = stats["total_texts"]
            with_pii = stats["texts_with_pii"]
            pct_pii = (with_pii / total * 100) if total > 0 else 0.0
            clean = total - with_pii
            pct_clean = 100.0 - pct_pii

            print("\n--- Batch PII Statistics Report ---")
            print(f"Total Texts Analyzed : {total}")
            print(f"Texts with PII       : {with_pii} ({pct_pii:.2f}%)")
            print(f"Clean Texts          : {clean} ({pct_clean:.2f}%)")
            print(f"Total Entities Found : {stats['total_entities']}")
            print(f"Unique Entity Types  : {stats['unique_entity_types']}")
            print("\nBreakdown by Label across Batch:")
            for label, count in stats["entity_counts"].items():
                print(f"  - {label}: {count}")

            if getattr(args, "verbose", False) and stats["total_entities"] > 0:
                print("\nExtracted Entities by Record:")
                for i, r in enumerate(result):
                    if r.has_pii:
                        print(f"  [Record #{i+1}] {r.text}")
                        for ent in r.entities:
                            print(f"    - [{ent.label}] '{ent.text}' (Score: {ent.score:.2%}, Offsets: {ent.start}-{ent.end})")
        else:
            stats = result.statistics
            print("\n--- PII Statistics Report ---")
            print(f"Total Entities : {stats['total_entities']}")
            print(f"Unique Types   : {stats['unique_entity_types']}")
            print(f"Text Density   : {stats['density']:.2%}")
            print(f"Avg Confidence : {stats['average_confidence']:.2%}")
            print("Breakdown by Label:")
            for label, count in stats["entity_counts"].items():
                print(f"  - {label}: {count}")

            if getattr(args, "verbose", False) and result.entities:
                print("\nExtracted Entities:")
                for ent in result.entities:
                    print(f"  - [{ent.label}] '{ent.text}' (Score: {ent.score:.2%}, Offsets: {ent.start}-{ent.end})")


if __name__ == "__main__":
    main()
```

---

## Step 6: End-to-End Example Script (`example.py`)

Create `example.py` in the root folder to demonstrate all 6 features:

```python
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
```

Run with `uv run`:
```powershell
uv run python example.py
```

---

## Step 7: Automated Testing with Pytest

Create `tests/test_detector.py`:

```python
import pytest
from ettin_pii import PIIDetector

@pytest.fixture(scope="session")
def detector():
    return PIIDetector(confidence_threshold=0.5)

def test_empty_string(detector):
    result = detector.detect("")
    assert result.num_entities == 0
    assert not result.has_pii
    assert result.statistics["total_entities"] == 0

def test_detection_and_redaction_strategies(detector):
    text = "Send credentials to bob@example.com immediately."
    result = detector.detect(text)

    assert result.has_pii
    assert "bob@example.com" not in result.redact(strategy="replace")
    assert "bob@example.com" not in result.redact(strategy="mask", mask_mode="full")
    assert "bob@example.com" not in result.redact(strategy="mask", mask_mode="alternate")
    assert "bob@example.com" not in result.redact(strategy="mask", mask_mode="first_only")

    # Custom mapping test
    custom_text = result.redact(strategy="custom", mapping={"email": "[PROTECTED_EMAIL]"})
    assert "[PROTECTED_EMAIL]" in custom_text

    # Fake preserves symbols (@, .) but scrambles characters
    faked = result.redact(strategy="fake")
    assert "bob@example.com" not in faked
    assert "@" in faked
    assert "." in faked

def test_batch_detection_and_export(detector):
    texts = ["Contact alice@test.com", "System reboot initiated.", "Call Bob at 555-9999"]
    batch = detector.detect(texts, batch_size=2)

    assert len(batch) == 3
    assert batch[0].has_pii
    assert not batch[1].has_pii
    assert batch[2].has_pii
    assert len(batch.redacted_texts) == 3
    assert batch.statistics["total_entities"] >= 2

    # Verify combined DataFrame export has text_index and source_text
    df = batch.to_dataframe()
    assert "text_index" in df.columns
    assert "source_text" in df.columns
    assert len(df) >= 2

def test_invalid_model_choice():
    with pytest.raises(ValueError, match="Invalid model"):
        PIIDetector(model="unsupported_model_size")
```

Run test suite:
```powershell
uv run pytest
```

---

## Step 8: CLI Usage Examples

Test the CLI directly using `uv run`:

```powershell
# 1. Detect PII inline with default model (small - 68M)
uv run ettin-pii detect "Call Dr. John at 555-0144"

# 2. Detect with ultra-fast nano model (17M)
uv run ettin-pii detect "Call Dr. John at 555-0144" --model nano

# 3. Redact text with partial asterisk masking using balanced tiny model (32M)
uv run ettin-pii redact "Call Dr. John at 555-0144" --model tiny --strategy mask --mask-mode first_only

# 4. Redact text with synthetic fake characters
uv run ettin-pii redact "Call Dr. John at 555-0144" --strategy fake

# 5. Redact and save to clean file
uv run ettin-pii redact input.txt --strategy replace --output clean.txt

# 6. Generate statistics report
uv run ettin-pii stats "John Doe, email: john@gmail.com, phone: 555-1234"

# 7. Generate statistics report with verbose entity listing
uv run ettin-pii stats "John Doe, email: john@gmail.com, phone: 555-1234" -v

# 8. Generate batch statistics report across multi-line file
uv run ettin-pii stats records.txt --batch

# 9. Generate batch statistics report with verbose entity listing by record
uv run ettin-pii stats records.txt --batch -v
```

---

## Why Github Repo is recommended for a Python library?

### Is creating a GitHub Repo necessary to publish on PyPI?
**Technically, No.** You do **not** need a GitHub repository to publish a package on PyPI.

You can build your files locally on your laptop (`uv build`) and upload them directly to PyPI (`uv publish`) using a PyPI account and API token. PyPI only cares about the packaged files (`.whl` and `.tar.gz`), not where your git code is hosted.

### Why You Still Should Create One:
Even though PyPI doesn't force you to have a GitHub repository, **nearly 100% of open-source Python libraries use one**. Here is why it is strongly recommended:

1. **User Trust & Credibility:**
   * Python developers are cautious about security. If someone finds `ettin-pii` on PyPI but cannot view the source code on GitHub, they usually won't install it.
2. **Issue Tracking & Feedback:**
   * GitHub provides an **Issues** tab where users can report bugs, request features, or ask how to use the library.
3. **PyPI Page Links:**
   * Having a GitHub repository lets you add clickable links right on your official PyPI page:
     * *Source Code / Homepage*
     * *Bug Tracker / Issues*
     * *Documentation*
4. **Automated Publishing (GitHub Actions / Trusted Publishing):**
   * Instead of manually running `uv publish` from your laptop, you can set up GitHub Actions so that whenever you create a release (e.g., `v0.1.0`), GitHub automatically runs your `pytest` suite and publishes to PyPI for you securely.

### How Your GitHub Repo Links in `pyproject.toml`
As configured in **Step 4**, the `[project.urls]` block inside `pyproject.toml` connects your GitHub repository directly to PyPI:

```toml
[project.urls]
Homepage = "https://github.com/kalyan-ks/ettin-pii"
Repository = "https://github.com/kalyan-ks/ettin-pii"
Issues = "https://github.com/kalyan-ks/ettin-pii/issues"
```

These links will then automatically show up as clickable buttons on your library's PyPI page!

---

## Step 9: Build and Distribution

When you are ready to distribute your package:

1. **Build wheel and source distributions:**
   ```powershell
   uv build
   ```
   Generates `.whl` and `.tar.gz` artifacts inside `dist/`.

---

### Step 1: Version Control with Git (Recommended Next Step)
Track your code and prepare it for collaboration:

1. **Initialize Git in the project root:**
   ```powershell
   git init
   ```

2. **Verify `.gitignore`:**
   Ensure heavy folders like `.venv/`, `dist/`, `.pytest_cache/`, and `__pycache__/` are ignored so they don't bloat the repository.

3. **Make the initial commit:**
   ```powershell
   git add .
   git commit -m "feat: initial implementation of ettin-pii v0.1.0"
   ```

---

### Step 2: Publish to GitHub
Host your open-source project publicly:

1. **Create a new repository on GitHub:**
   `https://github.com/kalyan-ks/ettin-pii`

2. **Connect your local repository and push:**
   ```powershell
   git remote add origin https://github.com/kalyan-ks/ettin-pii.git
   git branch -M main
   git push -u origin main
   ```

3. *(Optional)* Add a **GitHub Actions CI workflow** (`.github/workflows/tests.yml`) to automatically run `pytest` on every push or pull request.

---

### Step 3: Publish to PyPI (Python Package Index)
Make your library installable for anyone in the world via `pip install ettin-pii`:

1. **Test-Publish on TestPyPI (Recommended Safety Step):**
   * Create an account on [TestPyPI](https://test.pypi.org/) and generate an API token.
   * Upload your package using `uv`:
     ```powershell
     uv publish --publish-url https://test.pypi.org/legacy/ --token <TEST_PYPI_TOKEN>
     ```
   * Verify the download and package page on TestPyPI.

2. **Official PyPI Release:**
   * Create an account on [pypi.org](https://pypi.org/) and generate an API token.
   * Publish using `uv`:
     ```powershell
     uv publish --token <PYPI_TOKEN>
     ```
   * Once published, anyone can install and run your toolkit anywhere with:
     ```bash
     pip install ettin-pii
     ettin-pii detect "..."
     ```

---

## Feature Implementation Matrix

| Feature | Primary File | Key Methods / Properties |
| :--- | :--- | :--- |
| **1. Structured Results** | `src/ettin_pii/models.py` | `Entity`, `DetectionResult`, `BatchDetectionResult` |
| **2. Multi-Strategy Redactor** | `src/ettin_pii/redactor.py` | `result.redact(strategy="replace\|mask\|fake\|custom")` |
| **3. Multi-Model & Batching** | `src/ettin_pii/detector.py` | `model="small\|tiny\|nano"`, unified `detect()` (single & batch) |
| **4. Statistics & Density** | `src/ettin_pii/models.py` | `result.statistics` (counts, density, avg confidence) |
| **5. Multi-Format Export** | `src/ettin_pii/output/` | Single & Batch `.to_json()`, `.to_csv()`, `.to_dataframe()`, `.to_dict()` |
| **7. Command Line Tool** | `src/ettin_pii/cli.py` | `ettin-pii detect`, `ettin-pii redact`, `ettin-pii stats` |
