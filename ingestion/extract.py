"""Text extraction utilities."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

import pdfplumber
from docx import Document
from tika import parser


class ExtractionError(Exception):
    """Raised when text extraction fails."""


def extract_pdf(path: Path) -> str:
    with pdfplumber.open(path) as pdf:
        pages = [page.extract_text() or "" for page in pdf.pages]
    return "\n".join(pages)


def extract_docx(path: Path) -> str:
    document = Document(path)
    return "\n".join(paragraph.text for paragraph in document.paragraphs)


def extract_via_tika(path: Path) -> str:
    parsed = parser.from_file(str(path))
    return parsed.get("content", "") or ""


EXTRACTORS: dict[str, callable[[Path], str]] = {
    ".pdf": extract_pdf,
    ".docx": extract_docx,
    ".doc": extract_via_tika,
}


def extract_text(path: Path) -> str:
    extractor = EXTRACTORS.get(path.suffix.lower(), extract_via_tika)
    return extractor(path)


def batch_extract(paths: Iterable[Path]) -> dict[Path, str]:
    return {path: extract_text(path) for path in paths}
