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

