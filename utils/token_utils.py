"""
Utility: Token generation and validation helpers.
"""

import secrets
from database import get_db


def generate_token():
    """Generate a cryptographically secure 64-character hex token."""
    return secrets.token_hex(32)


def validate_token_from_request(request):
    """
    Extract and validate the top_token from a Flask request.
    Checks header 'top-token' first, then form/json 'token' field.
    Returns (token_string, device_document) or (None, None).
    """
    # Try header first
    token = request.headers.get("top-token", "")

    # Fallback to body
    if not token:
        if request.is_json:
            token = request.json.get("token", "")
        else:
            token = request.form.get("token", "")

    if not token:
        return None, None

    db = get_db()
    device = db.devices.find_one({"top_token": token})
    return token, device
