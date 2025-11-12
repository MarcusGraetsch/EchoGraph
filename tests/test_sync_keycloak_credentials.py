from __future__ import annotations

from unittest import mock

import pytest

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
    conn.autocommit = False

    result = synchronize_keycloak_credentials(conn, "keycloak", "secret", "keycloak")

    assert result == SyncResult(role_created=False, database_created=True)
    assert conn.autocommit is False


def test_synchronize_restores_autocommit_when_ensure_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    conn, _ = _prepare_conn()
    conn.autocommit = False

    def _boom(*_: object, **__: object) -> bool:
        raise RuntimeError("boom")

    monkeypatch.setattr("scripts.sync_keycloak_credentials.ensure_role", _boom)

    with pytest.raises(RuntimeError):
        synchronize_keycloak_credentials(conn, "keycloak", "secret", "keycloak")

    assert conn.autocommit is False


def test_autocommit_enabled_during_operations(monkeypatch: pytest.MonkeyPatch) -> None:
    conn, cursor = _prepare_conn()
    conn.autocommit = False

    def _assert_autocommit(*args: object, **kwargs: object) -> bool:
        assert args[0].autocommit is True
        return ensure_role(*args, **kwargs)

    monkeypatch.setattr("scripts.sync_keycloak_credentials.ensure_role", _assert_autocommit)

    cursor.fetchone.side_effect = [(1,), (1,)]

    synchronize_keycloak_credentials(conn, "keycloak", "secret", "keycloak")
    assert conn.autocommit is False
