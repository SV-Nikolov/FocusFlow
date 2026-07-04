from __future__ import annotations

from pathlib import Path

from focusflow.bootstrap import create_service_bundle


def test_sqlite_bootstrap_persists_users(tmp_path: Path) -> None:
    db_file = tmp_path / "focusflow-test.db"
    url = f"sqlite+pysqlite:///{db_file.as_posix()}"

    first = create_service_bundle(database_url=url)
    first.auth.register_user("alice", "StrongPass123")

    second = create_service_bundle(database_url=url)
    user = second.auth.authenticate_user("alice", "StrongPass123")

    assert user is not None
    assert user.username == "alice"


def test_bootstrap_falls_back_to_memory_on_invalid_url() -> None:
    bundle = create_service_bundle(database_url="not-a-valid-url", fallback_to_in_memory=True)

    assert bundle.backend_name == "in-memory"
    created = bundle.auth.register_user("bob", "StrongPass123")
    assert created.username == "bob"
