"""
MongoDB Database Connection & Helpers
"""

from pymongo import MongoClient
from config import MONGO_URI, MONGO_DB_NAME

# ═══════════════════════════════════════════════════════════
#  SINGLETON CONNECTION
# ═══════════════════════════════════════════════════════════
_client = None
_db = None


def get_db():
    """Return the MongoDB database instance (lazy-initialized singleton)."""
    global _client, _db
    if _db is None:
        _client = MongoClient(MONGO_URI)
        _db = _client[MONGO_DB_NAME]
        _ensure_indexes(_db)
    return _db


def _ensure_indexes(db):
    """Create indexes on first connection."""
    # devices collection
    db.devices.create_index("top_token", unique=True)
    db.devices.create_index("device_uid", unique=True)

    # accounts collection
    db.accounts.create_index("account_id", unique=True)
    db.accounts.create_index("device_token")
    db.accounts.create_index("pk")

    # orders collection
    db.orders.create_index("order_id", unique=True)
    db.orders.create_index("status")
    db.orders.create_index("order_type")

    # order_completions collection
    db.order_completions.create_index("order_id")
    db.order_completions.create_index("account_pk")

    # request deduplication
    db.submitted_requests.create_index("request_id", unique=True)


def close_db():
    """Close the MongoDB connection."""
    global _client, _db
    if _client:
        _client.close()
        _client = None
        _db = None
