"""Password-based encryption using PBKDF2 key derivation and Fernet (AES-256)."""

import base64
import os
import sys

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

SALT_LENGTH = 16
PBKDF2_ITERATIONS = 600_000
KEY_LENGTH = 32


def _derive_key(password: str, salt: bytes) -> bytes:
    """Derive a 256-bit Fernet-compatible key from a password and a random salt."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=KEY_LENGTH,
        salt=salt,
        iterations=PBKDF2_ITERATIONS,
    )
    return base64.urlsafe_b64encode(kdf.derive(password.encode("utf-8")))


def encrypt_message(message: str, password: str) -> bytes:
    """Encrypt a plaintext message with a user-supplied password.

    Returns the random salt (16 bytes) prepended to the Fernet token so that
    the same salt can be recovered during decryption without being stored
    separately.
    """
    if not message:
        raise ValueError("Message cannot be empty.")
    if not password:
        raise ValueError("Password cannot be empty.")

    salt = os.urandom(SALT_LENGTH)
    key = _derive_key(password, salt)
    token = Fernet(key).encrypt(message.encode("utf-8"))
    return salt + token


def decrypt_message(encrypted_bytes: bytes, password: str) -> str:
    """Decrypt bytes produced by :func:`encrypt_message` using the same password.

    Raises ``ValueError`` if the password is wrong or the data is corrupted
    (Fernet HMAC verification fails).
    """
    if not password:
        raise ValueError("Password cannot be empty.")
    if len(encrypted_bytes) < SALT_LENGTH + 1:
        raise ValueError("Encrypted data is too short or corrupted.")

    salt = encrypted_bytes[:SALT_LENGTH]
    token = encrypted_bytes[SALT_LENGTH:]
    key = _derive_key(password, salt)

    try:
        plaintext = Fernet(key).decrypt(token)
    except InvalidToken as exc:
        raise ValueError("Incorrect password or corrupted data.") from exc

    return plaintext.decode("utf-8")


if __name__ == "__main__":
    _msg = "Archimedes steganography test payload"
    _pwd = "correct-horse-battery-staple"

    try:
        _enc = encrypt_message(_msg, _pwd)
        _dec = decrypt_message(_enc, _pwd)
        assert _dec == _msg, "Round-trip mismatch"
        print("[PASS] Round-trip encrypt/decrypt")

        try:
            decrypt_message(_enc, "wrong-password")
            print("[FAIL] Wrong password should raise ValueError")
            sys.exit(1)
        except ValueError:
            print("[PASS] Wrong password rejected")

        print("All tests passed.")
        sys.exit(0)
    except Exception as exc:  # noqa: BLE001
        print(f"[FAIL] {exc}")
        sys.exit(1)
