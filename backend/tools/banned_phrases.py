from __future__ import annotations
import re
from memory.db import get_banned_phrases


def check_banned_phrases(text: str) -> list[str]:
    """Return list of banned phrases found in text (case-insensitive)."""
    phrases = [row["phrase"] for row in get_banned_phrases(active_only=True)]
    found = []
    text_lower = text.lower()
    for phrase in phrases:
        if re.search(re.escape(phrase), text_lower):
            found.append(phrase)
    return found


def strip_banned_phrases(text: str) -> tuple[str, list[str]]:
    """Remove banned phrases from text. Returns (cleaned_text, found_phrases)."""
    found = check_banned_phrases(text)
    cleaned = text
    for phrase in found:
        cleaned = re.sub(re.escape(phrase), "", cleaned, flags=re.IGNORECASE)
    return cleaned, found


def assert_no_banned_phrases(output: dict) -> list[str]:
    """
    Recursively walk a dict/list output and collect all banned phrase hits.
    Returns list of (field_path, phrase) strings for reporting.
    """
    hits: list[str] = []
    _walk(output, "", hits)
    return hits


def _walk(obj: object, path: str, hits: list[str]) -> None:
    if isinstance(obj, str):
        found = check_banned_phrases(obj)
        for phrase in found:
            hits.append(f"{path}: '{phrase}'")
    elif isinstance(obj, dict):
        for k, v in obj.items():
            _walk(v, f"{path}.{k}" if path else k, hits)
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            _walk(item, f"{path}[{i}]", hits)
