"""Crypto module."""

import base64
import os
import sys

from cryptography.fernet import Fernet
from cryptography.fernet import InvalidToken
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


KEY = None
SALT_SIZE = 16


def genkey(pw, salt=None):
    """Generate crypto key.

    Args:
        pw (str): password.
        salt (bytes): encryption salt. Default is None.

    Note:
        Code pulled directly from cryptography module docs.
    """
    if not salt:
        salt = os.urandom(SALT_SIZE)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(pw.encode("utf-8")))
    global KEY
    KEY = Fernet(key)
    KEY.salt = salt


def encrypt(s):
    """Return string s encrypted with salt prepended."""
    token = KEY.encrypt(s.encode("utf-8"))
    return KEY.salt + token


def decrypt(b, pw):
    salt = b[:SALT_SIZE]
    token = b[SALT_SIZE:]
    genkey(pw, salt=salt)
    try:
        return KEY.decrypt(token).decode()
    except InvalidToken:
        print("Incorrect password")
        sys.exit()
