"""Utilities for downloading document sources."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable

import requests


class DownloadError(Exception):
    """Raised when a download fails."""


def download_file(url: str, destination: Path, *, chunk_size: int = 16384) -> Path:
    """Download a single file and return its path."""
    response = requests.get(url, stream=True, timeout=60)
    try:
        response.raise_for_status()
    except requests.HTTPError as exc:
        raise DownloadError(f"Failed to download {url}: {exc}") from exc

    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("wb") as file_obj:
        for chunk in response.iter_content(chunk_size=chunk_size):
            if not chunk:
                continue
            file_obj.write(chunk)
    return destination


def download_all(urls: Iterable[str], output_dir: Path) -> list[Path]:
    """Download multiple files into an output directory."""
    downloaded: list[Path] = []
    for url in urls:
        filename = url.split("/")[-1]
        destination = output_dir / filename
        downloaded.append(download_file(url, destination))
    return downloaded
