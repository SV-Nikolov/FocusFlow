"""Authentication services for FocusFlow."""

from __future__ import annotations

import hashlib
import hmac
import secrets

from .exceptions import ValidationError
from .models import User


class PasswordHasher:
    """PBKDF2-based hasher suitable for a prototype authentication flow."""

    algorithm = "pbkdf2_sha256"
    iterations = 120_000
    salt_bytes = 16

    def hash_password(self, password: str) -> str:
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters.")
        salt = secrets.token_bytes(self.salt_bytes)
        digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, self.iterations)
        return f"{self.algorithm}${self.iterations}${salt.hex()}${digest.hex()}"

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

    def __init__(self, hasher: PasswordHasher | None = None) -> None:
        self._hasher = hasher or PasswordHasher()
        self._users_by_username: dict[str, User] = {}

    def register_user(self, username: str, password: str, email: str | None = None) -> User:
        username = username.strip()
        if not username:
            raise ValidationError("Username is required.")
        if username in self._users_by_username:
            raise ValidationError("Username already exists.")

        password_hash = self._hasher.hash_password(password)
        user = User(username=username, password_hash=password_hash, email=email)
        self._users_by_username[username] = user
        return user

    def authenticate_user(self, username: str, password: str) -> User | None:
        user = self._users_by_username.get(username)
        if user is None:
            return None
        if not self._hasher.verify_password(password, user.password_hash):
            return None
        return user

    def get_user(self, username: str) -> User | None:
        return self._users_by_username.get(username)
