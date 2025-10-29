#!/usr/bin/env python3
"""Export the Caddy internal CA certificate for trusting HTTPS locally."""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def export_certificate(output: Path) -> None:
  output.parent.mkdir(parents=True, exist_ok=True)
  command = [
      "docker",
      "compose",
      "cp",
      "caddy:/data/caddy/pki/authorities/local/root.crt",
      str(output),
  ]
  try:
      subprocess.run(command, check=True)
  except FileNotFoundError as error:
      raise SystemExit("docker is required to export the certificate") from error
  except subprocess.CalledProcessError as error:
      raise SystemExit(
          "failed to copy the Caddy root certificate; is the caddy service running?"
      ) from error


def main() -> None:
  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument(
      "--output",
      type=Path,
      default=Path("caddy-root.crt"),
      help="Path where the exported certificate should be written.",
  )
  args = parser.parse_args()
  export_certificate(args.output)
  print(f"Caddy root certificate exported to {args.output}")


if __name__ == "__main__":
  main()
