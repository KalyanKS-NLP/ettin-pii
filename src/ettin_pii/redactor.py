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
                f"Unknown mask_mode: '{mask_mode}'. Supported: 'full', 'alternate', 'first_only'."
            )

    @staticmethod
    def _fake_span(span_text: str) -> str:
        """
        Generates format-preserving pseudo-synthetic characters.
        Preserves original casing, digits, and special characters (like '@' or '.').
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

