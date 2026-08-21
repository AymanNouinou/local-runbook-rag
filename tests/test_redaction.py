from app.redaction import redact


def test_redacts_sensitive_values():
    text, count = redact("admin@example.com depuis 10.0.0.4 token=abc123")
    assert count == 3
    assert "admin@example.com" not in text
    assert "10.0.0.4" not in text
    assert "abc123" not in text
