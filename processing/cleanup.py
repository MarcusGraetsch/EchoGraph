"""Text normalization helpers."""
from __future__ import annotations

import re
import unicodedata
from typing import Iterable


WHITESPACE_RE = re.compile(r"\s+")


def normalize_text(text: str) -> str:
    """Normalize whitespace, unicode, and strip extraneous markers."""
    normalized = unicodedata.normalize("NFKC", text)
    normalized = normalized.replace("\u00ad", "")  # soft hyphen
    normalized = WHITESPACE_RE.sub(" ", normalized)
    return normalized.strip()


def normalize_many(texts: Iterable[str]) -> list[str]:
    return [normalize_text(text) for text in texts]
