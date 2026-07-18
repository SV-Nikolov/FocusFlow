"""Authentication services for FocusFlow."""

from __future__ import annotations

import hashlib
import hmac
import secrets

from .exceptions import ValidationError
from .models import User
from .repositories import InMemoryUserRepository, UserRepository


class PasswordHasher:
    """PBKDF2-based hasher suitable for a prototype authentication flow."""

    algorithm = "pbkdf2_sha256"
    iterations = 120_000
    salt_bytes = 16

    def hash_secret(self, value: str) -> str:
        """Securely hash a sensitive value without password-length validation."""
        salt = secrets.token_bytes(self.salt_bytes)
        digest = hashlib.pbkdf2_hmac(
            "sha256",
            value.encode("utf-8"),
            salt,
            self.iterations,
        )
        return (
            f"{self.algorithm}${self.iterations}$"
            f"{salt.hex()}${digest.hex()}"
        )

    def hash_password(self, password: str) -> str:
        """Validate and securely hash an account password."""
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters.")

        # Passwords use the same secure hash process after validation.
        return self.hash_secret(password)

    def verify_password(self, password: str, encoded_hash: str) -> bool:
        try:
            algorithm, iteration_text, salt_hex, digest_hex = encoded_hash.split("$", maxsplit=3)
        except ValueError:
            return False
        if algorithm != self.algorithm:
            return False
        try:
            iterations = int(iteration_text)
            salt = bytes.fromhex(salt_hex)
            expected_digest = bytes.fromhex(digest_hex)
        except ValueError:
            return False

        computed = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, iterations)
        return hmac.compare_digest(computed, expected_digest)


class AuthService:
    """In-memory user registration and login service for Phase I."""

    def __init__(
        self,
        hasher: PasswordHasher | None = None,
        user_repository: UserRepository | None = None,
    ) -> None:
        self._hasher = hasher or PasswordHasher()
        self._users = user_repository or InMemoryUserRepository()

    def register_user(
        self,
        username: str,
        password: str,
        email: str | None = None,
        security_question: str | None = None,
        security_answer: str | None = None,
    ) -> User:
        username = username.strip()
        if not username:
            raise ValidationError("Username is required.")
        if self._users.get_by_username(username) is not None:
            raise ValidationError("Username already exists.")

        if not security_question or not security_question.strip():
            raise ValidationError("Security question is required.")
        if not security_answer or not security_answer.strip():
            raise ValidationError("Security answer is required.")

        password_hash = self._hasher.hash_password(password)

        # Security answers may be shorter than eight characters, so they are
        # securely hashed without applying the account password length rule.
        security_answer_hash = self._hasher.hash_secret(
            security_answer.strip().lower()
        )

        user = User(
            username=username,
            password_hash=password_hash,
            email=email,
            security_question=security_question.strip(),
            security_answer_hash=security_answer_hash,
        )
        return self._users.save(user)

    def authenticate_user(self, username: str, password: str) -> User | None:
        user = self._users.get_by_username(username)
        if user is None:
            return None
        if not self._hasher.verify_password(password, user.password_hash):
            return None
        return user

    def get_user(self, username: str) -> User | None:
        return self._users.get_by_username(username)
    
    def get_security_question(self, username: str) -> str:
        user = self._users.get_by_username(username.strip())
        if user is None:
            raise ValidationError("Username was not found.")
        if not user.security_question:
            raise ValidationError(
                "This account does not have a security question."
            )
        return user.security_question

    def reset_password(
        self,
        username: str,
        security_answer: str,
        new_password: str,
    ) -> User:
        user = self._users.get_by_username(username.strip())
        if user is None:
            raise ValidationError("Username was not found.")

        if not user.security_answer_hash:
            raise ValidationError(
                "This account does not have password recovery configured."
            )

        normalized_answer = security_answer.strip().lower()
        if not self._hasher.verify_password(
            normalized_answer,
            user.security_answer_hash,
        ):
            raise ValidationError("The security answer is incorrect.")

        user.password_hash = self._hasher.hash_password(new_password)
        return self._users.save(user)
