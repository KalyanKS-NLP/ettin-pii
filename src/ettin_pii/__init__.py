"""
ettin-pii: Production-Ready PII Detection and Redaction Toolkit
"""
from .detector import PIIDetector
from .models import Entity, DetectionResult, BatchDetectionResult
from .redactor import Redactor

__version__ = "0.1.0"
__all__ = ["PIIDetector", "Entity", "DetectionResult", "BatchDetectionResult", "Redactor"]
