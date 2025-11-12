from __future__ import annotations

from unittest import mock

from psycopg import sql

from scripts.sync_keycloak_credentials import (
    SyncResult,
    ensure_database,
    ensure_role,
    synchronize_keycloak_credentials,
)


def _prepare_conn() -> tuple[mock.Mock, mock.Mock]:
    conn = mock.Mock()
    cursor = mock.Mock()
    cursor_cm = mock.MagicMock()
    cursor_cm.__enter__.return_value = cursor
    conn.cursor.return_value = cursor_cm
    return conn, cursor


def test_ensure_role_creates_when_missing() -> None:
    conn, cursor = _prepare_conn()
    cursor.fetchone.return_value = None

    created = ensure_role(conn, "keycloak", "secret")

    assert created is True
    cursor.execute.assert_any_call("SELECT 1 FROM pg_roles WHERE rolname = %s", ("keycloak",))
    create_call = cursor.execute.call_args_list[1]
    assert isinstance(create_call.args[0], sql.Composed)
    assert "CREATE ROLE" in repr(create_call.args[0])
    assert create_call.args[1] == ("secret",)


def test_ensure_role_updates_when_present() -> None:
    conn, cursor = _prepare_conn()
    cursor.fetchone.return_value = (1,)

    created = ensure_role(conn, "keycloak", "secret")

    assert created is False
    alter_call = cursor.execute.call_args_list[1]
    assert isinstance(alter_call.args[0], sql.Composed)
    assert "ALTER ROLE" in repr(alter_call.args[0])
    assert alter_call.args[1] == ("secret",)


def test_ensure_database_creates_when_missing() -> None:
    conn, cursor = _prepare_conn()
    cursor.fetchone.return_value = None

    created = ensure_database(conn, "keycloak", "keycloak")

    assert created is True
    create_call = cursor.execute.call_args_list[1]
    assert isinstance(create_call.args[0], sql.Composed)
    assert "CREATE DATABASE" in repr(create_call.args[0])


def test_ensure_database_updates_owner_when_present() -> None:
    conn, cursor = _prepare_conn()
    cursor.fetchone.return_value = (1,)

    created = ensure_database(conn, "keycloak", "keycloak")

    assert created is False
    alter_call = cursor.execute.call_args_list[1]
    assert isinstance(alter_call.args[0], sql.Composed)
    assert "ALTER DATABASE" in repr(alter_call.args[0])


def test_synchronize_returns_result_dataclass() -> None:
    conn, cursor = _prepare_conn()
    # First fetchone call -> role exists, second -> database missing
    cursor.fetchone.side_effect = [(1,), None]

    result = synchronize_keycloak_credentials(conn, "keycloak", "secret", "keycloak")

    assert result == SyncResult(role_created=False, database_created=True)
