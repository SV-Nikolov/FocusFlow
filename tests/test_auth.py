from focusflow.auth import AuthService, PasswordHasher
from focusflow.exceptions import ValidationError


def test_register_user_hashes_password() -> None:
    service = AuthService()

    user = service.register_user("alice", "StrongPass123")

    assert user.username == "alice"
    assert user.password_hash != "StrongPass123"
    assert "$" in user.password_hash


def test_register_rejects_duplicate_username() -> None:
    service = AuthService()
    service.register_user("alice", "StrongPass123")

    try:
        service.register_user("alice", "AnotherPass123")
        assert False, "Expected ValidationError"
    except ValidationError as exc:
        assert "exists" in str(exc)


def test_register_rejects_short_password() -> None:
    service = AuthService()

    try:
        service.register_user("alice", "short")
        assert False, "Expected ValidationError"
    except ValidationError as exc:
        assert "at least 8" in str(exc)


def test_authenticate_user_success_and_failure() -> None:
    service = AuthService(PasswordHasher())
    service.register_user("alice", "StrongPass123")

    user = service.authenticate_user("alice", "StrongPass123")
    wrong = service.authenticate_user("alice", "wrong-password")
    missing = service.authenticate_user("nobody", "StrongPass123")

    assert user is not None
    assert user.username == "alice"
    assert wrong is None
    assert missing is None
