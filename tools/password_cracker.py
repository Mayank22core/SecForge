"""
Password Hash Cracker Tool
Offline password hash testing using a wordlist.
Compares computed hashes of dictionary words against a target hash.
"""

import hashlib
import time


# Supported hash algorithms mapped to hashlib names
SUPPORTED_ALGORITHMS = {
    "MD5": "md5",
    "SHA-1": "sha1",
    "SHA-256": "sha256",
    "SHA-512": "sha512",
}


def hash_word(word, algorithm_key):
    """
    Hash a single word using the specified algorithm.

    Args:
        word: The word to hash (string)
        algorithm_key: Algorithm name (e.g., "MD5", "SHA-256")

    Returns:
        Hex digest string of the hash
    """
    algo_name = SUPPORTED_ALGORITHMS.get(algorithm_key)
    if not algo_name:
        raise ValueError(f"Unsupported algorithm: {algorithm_key}")

    h = hashlib.new(algo_name)
    # Hash the word as UTF-8 bytes
    h.update(word.encode("utf-8"))
    return h.hexdigest()


def validate_hash(hash_str, algorithm_key):
    """Validate that a hash string matches the expected length for the algorithm."""
    hash_str = hash_str.strip()
    expected_lengths = {
        "MD5": 32,
        "SHA-1": 40,
        "SHA-256": 64,
        "SHA-512": 128,
    }

    expected = expected_lengths.get(algorithm_key)
    if expected is None:
        return False, f"Unknown algorithm: {algorithm_key}"

    # Remove any whitespace or common prefixes
    hash_str = hash_str.replace(" ", "").lower()

    if len(hash_str) != expected:
        return False, (
            f"Invalid hash length for {algorithm_key}. "
            f"Expected {expected} characters, got {len(hash_str)}."
        )

    # Verify it's valid hex
    try:
        int(hash_str, 16)
    except ValueError:
        return False, f"Hash contains non-hex characters."

    return True, None


def load_wordlist(filepath):
    """
    Load a wordlist file and return a list of words.

    Reads the file line by line, strips whitespace, and skips empty lines.
    Handles encoding issues gracefully.

    Args:
        filepath: Path to the wordlist file

    Returns:
        List of words (strings)
    """
    import os

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Wordlist not found: {filepath}")

    words = []
    encodings = ["utf-8", "latin-1", "ascii"]

    for encoding in encodings:
        try:
            with open(filepath, "r", encoding=encoding) as f:
                for line in f:
                    word = line.strip()
                    if word:
                        words.append(word)
            return words
        except UnicodeDecodeError:
            continue

    raise ValueError(
        f"Could not read wordlist with any supported encoding.\n"
        f"File: {filepath}"
    )


def crack_hash(target_hash, algorithm_key, wordlist_path, callback=None, stop_event=None):
    """
    Attempt to crack a hash by comparing it against a wordlist.

    This is an OFFLINE cracking tool. It hashes each word from the
    wordlist using the same algorithm and compares it to the target hash.
    No network requests are made.

    Args:
        target_hash: The hash to crack (hex string)
        algorithm_key: Algorithm name (e.g., "MD5")
        wordlist_path: Path to a wordlist file (one word per line)
        callback: Function called with (words_tested, elapsed_time, current_word)
                  for progress updates
        stop_event: threading.Event to signal cancellation

    Returns:
        dict with keys:
            - found: bool
            - password: str or None
            - words_tested: int
            - elapsed_time: float (seconds)
            - status: str message
    """
    # Validate inputs
    target_hash = target_hash.strip().lower()
    valid, err = validate_hash(target_hash, algorithm_key)
    if not valid:
        raise ValueError(err)

    # Load the wordlist
    words = load_wordlist(wordlist_path)
    total_words = len(words)

    if total_words == 0:
        raise ValueError("Wordlist is empty")

    start_time = time.time()
    tested = 0

    # Test each word against the target hash
    for word in words:
        # Check if we should stop
        if stop_event and stop_event.is_set():
            elapsed = time.time() - start_time
            return {
                "found": False,
                "password": None,
                "words_tested": tested,
                "elapsed_time": elapsed,
                "status": "Search cancelled by user.",
            }

        # Hash the current word
        word_hash = hash_word(word, algorithm_key)

        # Compare with target hash (case-insensitive)
        if word_hash.lower() == target_hash.lower():
            elapsed = time.time() - start_time
            return {
                "found": True,
                "password": word,
                "words_tested": tested + 1,
                "elapsed_time": elapsed,
                "status": f"Password found: {word}",
            }

        tested += 1

        # Update progress periodically (every 100 words for efficiency)
        if callback and tested % 100 == 0:
            elapsed = time.time() - start_time
            callback(tested, elapsed, word)

    # No match found
    elapsed = time.time() - start_time
    return {
        "found": False,
        "password": None,
        "words_tested": tested,
        "elapsed_time": elapsed,
        "status": "Password not found in wordlist.",
    }


def create_sample_wordlist(filepath):
    """Create a small sample wordlist for testing purposes."""
    common_passwords = [
        "password", "123456", "12345678", "qwerty", "abc123",
        "monkey", "1234567", "letmein", "trustno1", "dragon",
        "baseball", "iloveyou", "master", "sunshine", "ashley",
        "bailey", "passw0rd", "shadow", "123123", "654321",
        "superman", "qazwsx", "michael", "football", "password1",
        "password123", "admin", "welcome", "hello", "charlie",
    ]

    with open(filepath, "w") as f:
        for word in common_passwords:
            f.write(word + "\n")

    return len(common_passwords)
