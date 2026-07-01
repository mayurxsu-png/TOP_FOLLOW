"""
Utility: Order stamp generation and verification.
Implements the SHA-256 stamp formula used by the TopFollow app.

Formula:
  SHA256(username + "|" + order_count + "|" + order_type + "|" + timestamp + "|tF_0rD3r_$tAmP_2024_sEcReT") + "_" + timestamp
"""

import hashlib
import time
from config import ORDER_STAMP_SECRET, STAMP_TIMESTAMP_TOLERANCE_SECONDS


def generate_order_stamp(username, order_count, order_type):
    """
    Generate a valid order stamp for the given parameters.
    Returns the stamp string.
    """
    timestamp = int(time.time())
    raw = f"{username}|{order_count}|{order_type}|{timestamp}|{ORDER_STAMP_SECRET}"
    hash_hex = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    return f"{hash_hex}_{timestamp}"


def verify_order_stamp(stamp, username, order_count, order_type):
    """
    Verify a submitted order stamp.
    Returns True if the stamp is valid within the timestamp tolerance window.
    """
    if not stamp or "_" not in stamp:
        return False

    parts = stamp.rsplit("_", 1)
    if len(parts) != 2:
        return False

    submitted_hash, timestamp_str = parts

    try:
        submitted_ts = int(timestamp_str)
    except ValueError:
        return False

    # Check timestamp is within tolerance
    current_ts = int(time.time())
    if abs(current_ts - submitted_ts) > STAMP_TIMESTAMP_TOLERANCE_SECONDS:
        return False

    # Recompute hash
    raw = f"{username}|{order_count}|{order_type}|{submitted_ts}|{ORDER_STAMP_SECRET}"
    expected_hash = hashlib.sha256(raw.encode("utf-8")).hexdigest()

    return submitted_hash == expected_hash
