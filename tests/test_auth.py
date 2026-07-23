from focusflow.auth import AuthService, PasswordHasher
from focusflow.exceptions import ValidationError

# Shared password recovery test data.
SECURITY_QUESTION = "What is your favorite color?"
SECURITY_ANSWER = "blue"


def test_register_user_hashes_password() -> None:
    service = AuthService()

    # Register a user together with password recovery information.
    user = service.register_user(
        "alice",
        "StrongPass123",
        security_question=SECURITY_QUESTION,
        security_answer=SECURITY_ANSWER,
    )

    assert user.username == "alice"
    assert user.password_hash != "StrongPass123"
    assert "$" in user.password_hash


def test_register_rejects_duplicate_username() -> None:
    service = AuthService()

    # Register the initial account before testing duplicate usernames.
    service.register_user(
        "alice",
        "StrongPass123",
        security_question=SECURITY_QUESTION,
        security_answer=SECURITY_ANSWER,
    )

    try:
        # Attempt to register another account using the same username.
        service.register_user(
            "alice",
            "AnotherPass123",
            security_question=SECURITY_QUESTION,
            security_answer=SECURITY_ANSWER,
        )
        assert False, "Expected ValidationError"
    except ValidationError as exc:
        assert "exists" in str(exc)


def test_register_rejects_short_password() -> None:
    service = AuthService()

    try:
        # Attempt to register with an invalid password.
        service.register_user(
            "alice",
            "short",
            security_question=SECURITY_QUESTION,
            security_answer=SECURITY_ANSWER,
        )
        assert False, "Expected ValidationError"
    except ValidationError as exc:
        assert "at least 8" in str(exc)


def test_authenticate_user_success_and_failure() -> None:
    service = AuthService(PasswordHasher())

    # Register a valid user before testing authentication.
    service.register_user(
        "alice",
        "StrongPass123",
        security_question=SECURITY_QUESTION,
        security_answer=SECURITY_ANSWER,
    )

    user = service.authenticate_user("alice", "StrongPass123")
    wrong = service.authenticate_user("alice", "wrong-password")
    missing = service.authenticate_user("nobody", "StrongPass123")

    assert user is not None
    assert user.username == "alice"
    assert wrong is None
    assert missing is None
