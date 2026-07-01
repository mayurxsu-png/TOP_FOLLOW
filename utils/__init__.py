"""
Utility: Token generation and validation.
"""

import secrets
from database import get_db


def generate_token():
    """Generate a 64-character hex token."""
    return secrets.token_hex(32)


def validate_token(token):
    """
    Validate a top_token. Returns the device document if valid, None otherwise.
    Checks both the 'top-token' header and form/json body 'token' field.
    """
    if not token:
        return None
    db = get_db()
    return db.devices.find_one({"top_token": token})
