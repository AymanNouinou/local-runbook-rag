import re


PATTERNS = (
    re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
    re.compile(r"(?i)\b(?:api[_-]?key|token|password|secret)\s*[:=]\s*\S+"),
)


def redact(text: str) -> tuple[str, int]:
    count = 0
    for pattern in PATTERNS:
        text, replacements = pattern.subn("[REDACTED]", text)
        count += replacements
    return text, count
