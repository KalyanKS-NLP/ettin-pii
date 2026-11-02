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

