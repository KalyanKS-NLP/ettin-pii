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

