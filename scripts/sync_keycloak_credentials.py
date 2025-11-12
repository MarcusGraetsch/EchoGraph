"""Utility for keeping the Keycloak database user in sync.

The deployment playbook provisions a dedicated PostgreSQL role and database for
Keycloak.  During testing we discovered that the previous shell based helper
occasionally sent an incomplete SQL script to ``psql`` which resulted in the
error::

    ERROR:  syntax error at or near "16694"

That failure prevented the Keycloak realm bootstrap from running which in turn
caused the frontend login redirect to return a 404.  This module replaces the
fragile shell snippets with parameterised ``psycopg`` queries so that
credentials are applied deterministically regardless of password contents.

The module can be executed directly or imported from other automation scripts.
It intentionally performs the minimal set of operations required for the
Keycloak container:

* create or update the ``keycloak`` role with the supplied password
* create the Keycloak database (defaults to ``keycloak``) and grant ownership

Example usage::

    python3 scripts/sync_keycloak_credentials.py \
        --postgres-url postgresql://postgres:postgres@localhost:5432/postgres \
        --keycloak-username keycloak \
        --keycloak-password s3cret \
        --keycloak-database keycloak
"""

from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass

import psycopg
from psycopg import sql


@dataclass(frozen=True)
class SyncResult:
    """Outcome of the synchronization run."""

    role_created: bool
    database_created: bool


def ensure_role(conn: psycopg.Connection, username: str, password: str) -> bool:
    """Create or update the PostgreSQL role used by Keycloak.

    Returns ``True`` when the role was created, ``False`` when it already
    existed and was merely updated.
    """

    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (username,))
        exists = cur.fetchone() is not None

        if not exists:
            cur.execute(
                sql.SQL("CREATE ROLE {} LOGIN PASSWORD %s").format(
                    sql.Identifier(username)
                ),
                (password,),
            )
            return True

        cur.execute(
            sql.SQL("ALTER ROLE {} WITH PASSWORD %s").format(
                sql.Identifier(username)
            ),
            (password,),
        )
        return False


def ensure_database(conn: psycopg.Connection, database: str, owner: str) -> bool:
    """Create the Keycloak database when missing and grant ownership."""

    with conn.cursor() as cur:
        cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (database,))
        exists = cur.fetchone() is not None

        if not exists:
            cur.execute(
                sql.SQL("CREATE DATABASE {} OWNER {} ENCODING 'UTF8'").format(
                    sql.Identifier(database), sql.Identifier(owner)
                )
            )
            created = True
        else:
            cur.execute(
                sql.SQL("ALTER DATABASE {} OWNER TO {}").format(
                    sql.Identifier(database), sql.Identifier(owner)
                )
            )
            created = False

        cur.execute(
            sql.SQL("GRANT ALL PRIVILEGES ON DATABASE {} TO {}").format(
                sql.Identifier(database), sql.Identifier(owner)
            )
        )

    return created


def synchronize_keycloak_credentials(
    conn: psycopg.Connection,
    username: str,
    password: str,
    database: str,
) -> SyncResult:
    """Ensure the Keycloak PostgreSQL role and database exist."""

    role_created = ensure_role(conn, username, password)
    database_created = ensure_database(conn, database, username)
    return SyncResult(role_created=role_created, database_created=database_created)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--postgres-url",
        default=
        os.environ.get("POSTGRES_URL")
        or os.environ.get("DATABASE_URL")
        or "postgresql://postgres:postgres@localhost:5432/postgres",
        help="DSN for the administrative PostgreSQL connection.",
    )
    parser.add_argument(
        "--keycloak-username",
        default=os.environ.get("KEYCLOAK_DB_USERNAME", "keycloak"),
        help="PostgreSQL role used by Keycloak (default: keycloak).",
    )
    parser.add_argument(
        "--keycloak-password",
        default=os.environ.get("KEYCLOAK_DB_PASSWORD"),
        help="Password assigned to the Keycloak PostgreSQL role.",
    )
    parser.add_argument(
        "--keycloak-database",
        default=os.environ.get("KEYCLOAK_DB_NAME", "keycloak"),
        help="Database name consumed by Keycloak (default: keycloak).",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.keycloak_password:
        parser.error(
            "--keycloak-password must be provided or set via KEYCLOAK_DB_PASSWORD"
        )

    try:
        with psycopg.connect(args.postgres_url) as conn:
            result = synchronize_keycloak_credentials(
                conn,
                username=args.keycloak_username,
                password=args.keycloak_password,
                database=args.keycloak_database,
            )
    except psycopg.Error as exc:  # pragma: no cover - defensive: network failures
        print(f"Failed to synchronize Keycloak credentials: {exc}", file=sys.stderr)
        return 1

    status_role = "created" if result.role_created else "updated"
    status_db = "created" if result.database_created else "updated"
    print(
        "Synchronized Keycloak database credentials (role {status_role}, database {status_db}).".format(
            status_role=status_role,
            status_db=status_db,
        )
    )
    return 0


if __name__ == "__main__":  # pragma: no cover - entrypoint convenience
    sys.exit(main())
