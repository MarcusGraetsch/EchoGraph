#!/usr/bin/env python3
"""Export the Caddy internal CA certificate for trusting HTTPS locally."""
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path
from typing import Iterable


def _run_compose(*args: str, capture: bool = False) -> subprocess.CompletedProcess:
  return subprocess.run(
      ["docker", "compose", *args],
      check=False,
      capture_output=capture,
      text=capture,
  )


def _ensure_caddy_container() -> str:
  """Return the running container ID for the caddy service."""

  result = _run_compose("ps", "-q", "caddy", capture=True)
  if result.returncode != 0:
      raise SystemExit(result.stderr.strip() or "failed to query docker compose state")

  container_id = result.stdout.strip()
  if container_id:
      return container_id

  # Attempt to start the service automatically if it isn't running yet.
  start = _run_compose("up", "-d", "caddy", capture=True)
  if start.returncode != 0:
      raise SystemExit(
          start.stderr.strip()
          or "failed to start the caddy service; run 'docker compose up -d caddy'"
      )

  follow_up = _run_compose("ps", "-q", "caddy", capture=True)
  if follow_up.returncode != 0:
      raise SystemExit(
          follow_up.stderr.strip() or "unable to locate the running caddy container"
      )

  container_id = follow_up.stdout.strip()
  if not container_id:
      raise SystemExit("the caddy service is not running; run 'docker compose up -d caddy'")

  return container_id


def _try_copy(container_id: str, paths: Iterable[str], output: Path) -> bool:
  for relative in paths:
      command = ["docker", "cp", f"{container_id}:{relative}", str(output)]
      completed = subprocess.run(command, check=False)
      if completed.returncode == 0:
          return True
  return False


def export_certificate(output: Path) -> None:
  output.parent.mkdir(parents=True, exist_ok=True)
  candidate_paths = (
      "/data/pki/authorities/local/root.crt",
      # Older compose bundles mounted the Caddy data directory under /data/caddy.
      "/data/caddy/pki/authorities/local/root.crt",
  )

  try:
      container_id = _ensure_caddy_container()
      if _try_copy(container_id, candidate_paths, output):
          return
  except FileNotFoundError as error:
      raise SystemExit("docker is required to export the certificate") from error

  raise SystemExit(
      "no internal Caddy certificate was found. If you configured public TLS or "
      "disabled HTTPS, run the stack without 'CADDY_TLS_DIRECTIVE' so the "
      "internal CA is generated, then retry."
  )


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
