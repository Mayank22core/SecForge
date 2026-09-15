"""
AES Encryption/Decryption Tool
Secure AES-GCM encryption/decryption using the cryptography package.
Supports both text and file encryption with password-based key derivation.
"""

import os
import base64


def check_cryptography():
    """Check if the cryptography package is installed."""
    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM  # noqa: F401
        return True, ""
    except ImportError:
        return False, "cryptography package not installed. Run: pip install cryptography"


def derive_key(password, salt):
    """
    Derive an AES-256 key from a password using Scrypt KDF.

    Scrypt is a memory-hard key derivation function designed to be
    resistant to hardware brute-force attacks. It's more secure than
    PBKDF2 for password-based key derivation.

    Args:
        password: The user's password string
        salt: Random salt bytes (16 bytes recommended)

    Returns:
        32-byte key suitable for AES-256
    """
    from cryptography.hazmat.primitives.kdf.scrypt import Scrypt

    kdf = Scrypt(
        salt=salt,
        length=32,  # 256-bit key for AES-256
        n=2**14,    # CPU/memory cost parameter
        r=8,        # Block size
        p=1,        # Parallelization parameter
    )
    return kdf.derive(password.encode("utf-8"))


def encrypt_text(plaintext, password):
    """
    Encrypt plaintext using AES-256-GCM with a password.

    AES-GCM is an authenticated encryption mode that provides both
    confidentiality (encryption) and integrity (authentication).
    Any tampering with the ciphertext will be detected during decryption.

    The output format is: salt (16 bytes) + nonce (12 bytes) + ciphertext + tag (16 bytes)

    Args:
        plaintext: The text to encrypt
        password: The encryption password

    Returns:
        Base64-encoded encrypted data
    """
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM

    if not password:
        raise ValueError("Password cannot be empty")
    if not plaintext:
        raise ValueError("Plaintext cannot be empty")

    # Generate random salt and nonce (IV)
    # Salt is used for key derivation, nonce ensures same plaintext
    # produces different ciphertext each time
    salt = os.urandom(16)
    nonce = os.urandom(12)  # 96-bit nonce recommended for GCM

    # Derive the encryption key from the password
    key = derive_key(password, salt)

    # Create AES-GCM cipher and encrypt
    # GCM mode produces ciphertext + authentication tag
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, plaintext.encode("utf-8"), None)

    # Combine salt + nonce + ciphertext (which includes the tag)
    encrypted = salt + nonce + ciphertext
    return base64.b64encode(encrypted).decode("ascii")


def decrypt_text(encrypted_b64, password):
    """
    Decrypt base64-encoded AES-256-GCM encrypted data.

    Args:
        encrypted_b64: Base64-encoded encrypted data
        password: The decryption password

    Returns:
        Decrypted plaintext string
    """
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.exceptions import InvalidTag

    if not password:
        raise ValueError("Password cannot be empty")
    if not encrypted_b64:
        raise ValueError("Encrypted data cannot be empty")

    try:
        encrypted = base64.b64decode(encrypted_b64)
    except Exception:
        raise ValueError("Invalid base64 data")

    # Minimum size: 16 (salt) + 12 (nonce) + 16 (tag) = 44 bytes
    if len(encrypted) < 44:
        raise ValueError("Encrypted data is too short or corrupted")

    # Extract salt, nonce, and ciphertext+tag
    salt = encrypted[:16]
    nonce = encrypted[16:28]
    ciphertext_with_tag = encrypted[28:]

    # Derive the same key from password and salt
    key = derive_key(password, salt)

    # Decrypt and verify authentication tag
    aesgcm = AESGCM(key)
    try:
        plaintext = aesgcm.decrypt(nonce, ciphertext_with_tag, None)
    except InvalidTag:
        raise ValueError(
            "Decryption failed. Wrong password or corrupted data."
        )

    return plaintext.decode("utf-8")


def encrypt_file(input_path, output_path, password):
    """
    Encrypt a file using AES-256-GCM.

    Reads the entire file, encrypts it, and writes the result.
    The output file contains: salt + nonce + ciphertext + tag.

    Args:
        input_path: Path to the file to encrypt
        output_path: Path to write the encrypted file
        password: The encryption password
    """
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM

    if not password:
        raise ValueError("Password cannot be empty")

    if not os.path.exists(input_path):
        raise FileNotFoundError(f"File not found: {input_path}")

    # Read the original file content
    with open(input_path, "rb") as f:
        file_data = f.read()

    if not file_data:
        raise ValueError("File is empty")

    # Generate random salt and nonce
    salt = os.urandom(16)
    nonce = os.urandom(12)

    # Derive key and encrypt
    key = derive_key(password, salt)
    aesgcm = AESGCM(key)
    ciphertext = aesgcm.encrypt(nonce, file_data, None)

    # Write encrypted data
    with open(output_path, "wb") as f:
        f.write(salt + nonce + ciphertext)


def decrypt_file(input_path, output_path, password):
    """
    Decrypt an AES-256-GCM encrypted file.

    Args:
        input_path: Path to the encrypted file
        output_path: Path to write the decrypted file
        password: The decryption password
    """
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
    from cryptography.exceptions import InvalidTag

    if not password:
        raise ValueError("Password cannot be empty")

    if not os.path.exists(input_path):
        raise FileNotFoundError(f"File not found: {input_path}")

    with open(input_path, "rb") as f:
        encrypted_data = f.read()

    if len(encrypted_data) < 44:
        raise ValueError("Encrypted file is too short or corrupted")

    # Extract components
    salt = encrypted_data[:16]
    nonce = encrypted_data[16:28]
    ciphertext_with_tag = encrypted_data[28:]

    # Derive key and decrypt
    key = derive_key(password, salt)
    aesgcm = AESGCM(key)

    try:
        plaintext = aesgcm.decrypt(nonce, ciphertext_with_tag, None)
    except InvalidTag:
        raise ValueError(
            "Decryption failed. Wrong password or corrupted file."
        )

    with open(output_path, "wb") as f:
        f.write(plaintext)
