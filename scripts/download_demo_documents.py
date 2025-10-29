"""Utility script to download a lightweight demo dataset."""
from __future__ import annotations

import argparse
import pathlib
import textwrap
from collections.abc import Iterable, Sequence

import requests
from requests import exceptions as requests_exceptions

DEMO_SOURCES: dict[str, Sequence[str]] = {
    "aws_well_architected.pdf": (
        # Primary source hosted by AWS.
        "https://d1.awsstatic.com/whitepapers/architecture/AWS_Well-Architected_Framework.pdf",
        # Public mirror that has proven reliable historically.
        "https://public-docs.s3.amazonaws.com/aws/AWS_Well-Architected_Framework.pdf",
    ),
    "nist_800_53.docx": (
        # Sample policy document provided by the CISA repository.
        "https://csrc.nist.gov/csrc/media/Publications/sp/800-53/rev-5/final/docx/sp800-53r5-docx.docx",
        # Fallback generic template if the official source is unavailable.
        "https://filesamples.com/samples/document/docx/sample1.docx",
    ),
}


def download_file(url: str, destination: pathlib.Path) -> None:
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    destination.write_bytes(response.content)


def ensure_directory(path: pathlib.Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def main(urls: Iterable[tuple[str, Sequence[str]]], output: pathlib.Path) -> None:
    ensure_directory(output)
    failures: list[tuple[str, Sequence[str]]] = []
    for filename, candidates in urls:
        target = output / filename
        print(f"Downloading {filename} -> {target}")
        for url in candidates:
            try:
                download_file(url, target)
            except requests_exceptions.HTTPError as exc:
                print(f"  ! HTTP {exc.response.status_code} from {url}; trying next mirror")
                continue
            except requests_exceptions.RequestException as exc:  # pragma: no cover - network specific
                print(f"  ! Failed to download from {url}: {exc}")
                continue
            else:
                break
        else:
            failures.append((filename, candidates))
            print(f"  ! Skipped {filename}; no mirrors succeeded")
    if failures:
        failed_list = "\n".join(
            f"  - {filename}: {', '.join(candidates)}" for filename, candidates in failures
        )
        print(
            "\nThe following demo files could not be downloaded:\n"
            f"{failed_list}\n"
            "You can update scripts/download_demo_documents.py with alternative mirrors or "
            "place your own documents into the output directory manually."
        )

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
    main(DEMO_SOURCES.items(), args.output)
