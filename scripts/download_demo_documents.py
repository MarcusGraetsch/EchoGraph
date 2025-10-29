"""Utility script to download a lightweight demo dataset."""
from __future__ import annotations

import argparse
import base64
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

BUNDLED_ASSETS: dict[str, str] = {
    "aws_well_architected.pdf": (
        "JVBERi0xLjQKMSAwIG9iago8PCAvVHlwZSAvQ2F0YWxvZyAvUGFnZXMgMiAwIFIgPj4KZW5kb2Jq"
        "CjIgMCBvYmoKPDwgL1R5cGUgL1BhZ2VzIC9Db3VudCAxIC9LaWRzIFszIDAgUl0gPj4KZW5kb2Jq"
        "CjMgMCBvYmoKPDwgL1R5cGUgL1BhZ2UgL1BhcmVudCAyIDAgUiAvTWVkaWFCb3ggWzAgMCA2MTIg"
        "NzkyXSAvQ29udGVudHMgNCAwIFIgL1Jlc291cmNlcyA8PCAvRm9udCA8PCAvRjEgNSAwIFIgPj4g"
        "Pj4gPj4KZW5kb2JqCjQgMCBvYmoKPDwgL0xlbmd0aCA1NSA+PgpzdHJlYW0KQlQKL0YxIDI0IFRm"
        "CjcyIDcwMCBUZAooRXhhbXBsZSBQREYpIFRqCkVUCmVuZHN0cmVhbQplbmRvYmoKNSAwIG9iago8"
        "PCAvVHlwZSAvRm9udCAvU3VidHlwZSAvVHlwZTEgL0Jhc2VGb250IC9IZWx2ZXRpY2EgPj4KZW5k"
        "b2JqCnhyZWYKMCA2CjAwMDAwMDAwMDAgNjU1MzUgZiAKMDAwMDAwMDAxMCAwMDAwMCBuIAowMDAw"
        "MDAwMDY3IDAwMDAwIG4gCjAwMDAwMDAxMjggMDAwMDAgbiAKMDAwMDAwMDI3NyAwMDAwMCBuIAow"
        "MDAwMDAwMzc0IDAwMDAwIG4gCnRyYWlsZXIKPDwgL1NpemUgNiAvUm9vdCAxIDAgUiA+PgpzdGFy"
        "dHhyZWYKNDQwCiUlRU9GCg=="
    ),
    "nist_800_53.docx": (
        "UEsDBBQAAAAAAHxbXVskkqSerQEAAK0BAAATAAAAW0NvbnRlbnRfVHlwZXNdLnhtbDw/eG1sIHZl"
        "cnNpb249IjEuMCIgZW5jb2Rpbmc9IlVURi04Ij8+CjxUeXBlcyB4bWxucz0iaHR0cDovL3NjaGVt"
        "YXMub3BlbnhtbGZvcm1hdHMub3JnL3BhY2thZ2UvMjAwNi9jb250ZW50LXR5cGVzIj4KICAgIDxE"
        "ZWZhdWx0IEV4dGVuc2lvbj0icmVscyIgQ29udGVudFR5cGU9ImFwcGxpY2F0aW9uL3ZuZC5vcGVu"
        "eG1sZm9ybWF0cy1wYWNrYWdlLnJlbGF0aW9uc2hpcHMreG1sIi8+CiAgICA8RGVmYXVsdCBFeHRl"
        "bnNpb249InhtbCIgQ29udGVudFR5cGU9ImFwcGxpY2F0aW9uL3htbCIvPgogICAgPE92ZXJyaWRl"
        "IFBhcnROYW1lPSIvd29yZC9kb2N1bWVudC54bWwiIENvbnRlbnRUeXBlPSJhcHBsaWNhdGlvbi92"
        "bmQub3BlbnhtbGZvcm1hdHMtb2ZmaWNlZG9jdW1lbnQud29yZHByb2Nlc3NpbmdtbC5kb2N1bWVu"
        "dC5tYWluK3htbCIvPgo8L1R5cGVzPlBLAwQUAAAAAAB8W11buNRKvB0BAAAdAQAACwAAAF9yZWxz"
        "Ly5yZWxzPD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0iVVRGLTgiPz4KPFJlbGF0aW9uc2hp"
        "cHMgeG1sbnM9Imh0dHA6Ly9zY2hlbWFzLm9wZW54bWxmb3JtYXRzLm9yZy9wYWNrYWdlLzIwMDYv"
        "cmVsYXRpb25zaGlwcyI+CiAgICA8UmVsYXRpb25zaGlwIElkPSJSMSIgVHlwZT0iaHR0cDovL3Nj"
        "aGVtYXMub3BlbnhtbGZvcm1hdHMub3JnL29mZmljZURvY3VtZW50LzIwMDYvcmVsYXRpb25zaGlw"
        "cy9vZmZpY2VEb2N1bWVudCIgVGFyZ2V0PSJ3b3JkL2RvY3VtZW50LnhtbCIvPgo8L1JlbGF0aW9u"
        "c2hpcHM+UEsDBBQAAAAAAHxbXVv/keLmCwEAAAsBAAARAAAAd29yZC9kb2N1bWVudC54bWw8P3ht"
        "bCB2ZXJzaW9uPSIxLjAiIGVuY29kaW5nPSJVVEYtOCI/Pgo8dzpkb2N1bWVudCB4bWxuczp3PSJo"
        "dHRwOi8vc2NoZW1hcy5vcGVueG1sZm9ybWF0cy5vcmcvd29yZHByb2Nlc3NpbmdtbC8yMDA2L21h"
        "aW4iPgogIDx3OmJvZHk+CiAgICA8dzpwPgogICAgICA8dzpyPgogICAgICAgIDx3OnQ+U2FtcGxl"
        "IE5JU1QgODAwLTUzIGV4Y2VycHQ8L3c6dD4KICAgICAgPC93OnI+CiAgICA8L3c6cD4KICAgIDx3"
        "OnNlY3RQci8+CiAgPC93OmJvZHk+Cjwvdzpkb2N1bWVudD5QSwECFAMUAAAAAAB8W11bJJKknq0B"
        "AACtAQAAEwAAAAAAAAAAAAAAIABAAAAAAF9Db250ZW50X1R5cGVzXS54bWxQSwECFAMUAAAAAAB8"
        "W11buNRKvB0BAAAdAQAACwAAAAAAAAAAAAAAIAB3gEAAF9yZWxzLy5yZWxzUEsBAhQDFAAAAAAAfF"
        "tdW/+R4uYLAQAACwEAAAEQAAAAAAAAAAAAAACAAEkAwAAd29yZC9kb2N1bWVudC54bWxQSwUGAAAA"
        "AAMAAwC5AAAAXgQAAAAA=="
    ),
}


def download_file(url: str, destination: pathlib.Path) -> None:
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    destination.write_bytes(response.content)


def ensure_directory(path: pathlib.Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def main(
    urls: Iterable[tuple[str, Sequence[str]]],
    output: pathlib.Path,
    *,
    prefer_local_assets: bool = True,
) -> None:
    ensure_directory(output)
    failures: list[tuple[str, Sequence[str]]] = []
    for filename, candidates in urls:
        target = output / filename
        print(f"Downloading {filename} -> {target}")
        asset_data = BUNDLED_ASSETS.get(filename)
        if prefer_local_assets and asset_data:
            target.write_bytes(base64.b64decode(asset_data))
            print("  ✓ Wrote bundled demo asset")
            continue
        last_error: str | None = None
        for url in candidates:
            try:
                download_file(url, target)
            except requests_exceptions.HTTPError as exc:
                last_error = f"HTTP {exc.response.status_code} from {url}"
                continue
            except requests_exceptions.RequestException as exc:  # pragma: no cover - network specific
                last_error = f"Failed to download from {url}: {exc}"
                continue
            else:
                break
        else:
            if asset_data:
                target.write_bytes(base64.b64decode(asset_data))
                print(
                    "  ✓ Wrote bundled demo asset after remote mirrors were unavailable"
                )
                continue
            failures.append((filename, candidates))
            error_message = last_error or "no mirrors succeeded"
            print(f"  ! Skipped {filename}; {error_message}")
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
    parser.add_argument(
        "--prefer-remote",
        action="store_true",
        help="Attempt remote mirrors before using bundled demo assets.",
    )
    args = parser.parse_args()
    main(
        DEMO_SOURCES.items(),
        args.output,
        prefer_local_assets=not args.prefer_remote,
    )
