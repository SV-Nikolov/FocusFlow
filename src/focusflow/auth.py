"""Authentication and password-recovery services for FocusFlow."""

from __future__ import annotations

import hashlib
import hmac
import secrets

from .exceptions import ValidationError
from .models import User
from .repositories import InMemoryUserRepository, UserRepository


class PasswordHasher:
    """PBKDF2-based hasher for passwords and security answers."""

    algorithm = "pbkdf2_sha256"
    iterations = 120_000
    salt_bytes = 16

    def hash_password(self, password: str) -> str:
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters.")
        salt = secrets.token_bytes(self.salt_bytes)
        digest = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt, self.iterations
        )
        return f"{self.algorithm}${self.iterations}${salt.hex()}${digest.hex()}"

    def verify_password(self, password: str, encoded_hash: str) -> bool:
        try:
            algorithm, iteration_text, salt_hex, digest_hex = encoded_hash.split(
                "$", maxsplit=3
            )
            iterations = int(iteration_text)
            salt = bytes.fromhex(salt_hex)
            expected_digest = bytes.fromhex(digest_hex)
        except (ValueError, TypeError):
            return False

        if algorithm != self.algorithm:
            return False

        computed = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), salt, iterations
        )
        return hmac.compare_digest(computed, expected_digest)


class AuthService:
    """Registration, login, security-question lookup, and password reset."""

    def __init__(
        self,
        hasher: PasswordHasher | None = None,
        user_repository: UserRepository | None = None,
    ) -> None:
        self._hasher = hasher or PasswordHasher()
        self._users = user_repository or InMemoryUserRepository()

    @staticmethod
    def _normalize_security_answer(answer: str) -> str:
        return " ".join(answer.strip().casefold().split())

    def register_user(
        self,
        username: str,
        password: str,
        security_question: str,
        security_answer: str,
        email: str | None = None,
    ) -> User:
        username = username.strip()
        security_question = security_question.strip()
        normalized_answer = self._normalize_security_answer(security_answer)

        if not username:
            raise ValidationError("Username is required.")
        if self._users.get_by_username(username) is not None:
            raise ValidationError("Username already exists.")
        if not security_question:
            raise ValidationError("A security question is required.")
        if len(normalized_answer) < 3:
            raise ValidationError(
                "The security answer must contain at least 3 characters."
            )

        user = User(
            username=username,
            password_hash=self._hasher.hash_password(password),
            security_question=security_question,
            security_answer_hash=self._hasher.hash_password(normalized_answer),
            email=email.strip() if email else None,
        )
        return self._users.save(user)

    def authenticate_user(self, username: str, password: str) -> User | None:
        user = self._users.get_by_username(username.strip())
        if user is None:
            return None
        if not self._hasher.verify_password(password, user.password_hash):
            return None
        return user

    def get_user(self, username: str) -> User | None:
        return self._users.get_by_username(username.strip())

    def get_security_question(self, username: str) -> str:
        user = self._users.get_by_username(username.strip())
        if user is None or not user.security_question:
            raise ValidationError("Account recovery is not available for this account.")
        return user.security_question

    def reset_password(
        self,
        *,
        username: str,
        security_answer: str,
        new_password: str,
    ) -> User:
        user = self._users.get_by_username(username.strip())
        generic_error = "The username or security answer is incorrect."
        if user is None or not user.security_answer_hash:
            raise ValidationError(generic_error)

        normalized_answer = self._normalize_security_answer(security_answer)
        if not self._hasher.verify_password(
            normalized_answer, user.security_answer_hash
        ):
            raise ValidationError(generic_error)

        user.password_hash = self._hasher.hash_password(new_password)
        return self._users.save(user)
