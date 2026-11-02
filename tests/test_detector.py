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

