"""Utility script to download a lightweight demo dataset."""
from __future__ import annotations

import argparse
import pathlib
import textwrap
from typing import Iterable

import requests

DEMO_URLS = {
    "aws_well_architected.pdf": "https://raw.githubusercontent.com/hwchase17/langchain/master/docs/docs/modules/state_of_the_union.pdf",
    "nist_800_53.docx": "https://github.com/looker-open-source/lookml-intro/raw/master/sample_docs/sample_doc.docx",
}


def download_file(url: str, destination: pathlib.Path) -> None:
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    destination.write_bytes(response.content)


def ensure_directory(path: pathlib.Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def main(urls: Iterable[tuple[str, str]], output: pathlib.Path) -> None:
    ensure_directory(output)
    for filename, url in urls:
        target = output / filename
        print(f"Downloading {filename} -> {target}")
        download_file(url, target)
    readme = output / "README.md"
    readme.write_text(
        textwrap.dedent(
            """
            # Demo Documents

            The files in this directory are sourced from public URLs and are intended for
            development and testing purposes only. Do not redistribute outside of the
            repository without verifying license compatibility.
            """
        ).strip()
        + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download demo regulatory documents")
    parser.add_argument("--output", type=pathlib.Path, default=pathlib.Path("data/demo_docs"))
    args = parser.parse_args()
    main(DEMO_URLS.items(), args.output)
