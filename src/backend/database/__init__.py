import os
import sqlite3
import hashlib
from pathlib import Path
from cryptography.fernet import Fernet, InvalidToken
from dotenv import load_dotenv
from config import ENCRYPTION_KEY

if not ENCRYPTION_KEY:
    raise ValueError("ENCRYPTION_KEY is not set.")
try:
    fernet = Fernet(ENCRYPTION_KEY)
except Exception as e:
    raise ValueError(f"Invalid ENCRYPTION_KEY: {e}")

# DB path
DB_FILE = Path(__file__).resolve().parents[3] / "data" / "api_keys.db"
DB_FILE.parent.mkdir(parents=True, exist_ok=True)


def init_db():
    """(Re)create the API keys table with proper constraints"""
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("DROP TABLE IF EXISTS api_keys")
        c.execute(
            """
            CREATE TABLE api_keys (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                encrypted_key TEXT NOT NULL,
                key_hash TEXT NOT NULL UNIQUE
            )
        """
        )
        conn.commit()


def normalize_key(plain_key: str) -> str:
    """Normalize API key by stripping whitespace."""
    return plain_key.strip()


def encrypt_key(plain_key: str) -> str:
    """Encrypt API key using Fernet."""
    return fernet.encrypt(plain_key.encode()).decode()


def decrypt_key(encrypted_key: str) -> str:
    """Decrypt Fernet-encrypted API key."""
    return fernet.decrypt(encrypted_key.encode()).decode()


def hash_key(plain_key: str) -> str:
    """Hash plain API key (normalized)."""
    normalized = normalize_key(plain_key)
    return hashlib.sha256(normalized.encode()).hexdigest()


def add_api_key(plain_key: str) -> bool:
    """Encrypt and insert API key if not already in DB."""
    plain_key = normalize_key(plain_key)
    encrypted = encrypt_key(plain_key)
    key_hash = hash_key(plain_key)

    try:
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute(
                "INSERT INTO api_keys (encrypted_key, key_hash) VALUES (?, ?)",
                (encrypted, key_hash),
            )
            conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False  # Duplicate detected


def check_api_key(plain_key: str) -> bool:
    """Check if plain API key exists (by hash)."""
    key_hash = hash_key(plain_key)
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("SELECT 1 FROM api_keys WHERE key_hash = ?", (key_hash,))
        return c.fetchone() is not None
