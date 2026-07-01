"""
Data models — thin wrappers around MongoDB operations.
Each function maps to a specific business action on the database.
"""

import secrets
import time
import random
from datetime import datetime, timezone
from database import get_db
from config import INITIAL_COINS, COIN_REWARD_PER_TASK


# ═══════════════════════════════════════════════════════════
#  DEVICE OPERATIONS
# ═══════════════════════════════════════════════════════════

def create_device(device_uid, android_id, aaid, app_version, app_source, language, fcm_token=""):
    """Register a new device and return its document (with top_token)."""
    db = get_db()

    # Check if device already registered
    existing = db.devices.find_one({"device_uid": device_uid})
    if existing:
        return existing

    top_token = secrets.token_hex(32)  # 64-char hex string

    doc = {
        "device_uid": device_uid,
        "android_id": android_id,
        "aaid": aaid,
        "top_token": top_token,
        "coin": INITIAL_COINS,
        "app_version": int(app_version) if app_version else 17,
        "app_source": app_source or "apk",
        "language": language or "en",
        "fcm_token": fcm_token or "",
        "created_at": datetime.now(timezone.utc),
    }

    db.devices.insert_one(doc)
    return doc


def get_device_by_token(token):
    """Look up a device by its top_token."""
    db = get_db()
    return db.devices.find_one({"top_token": token})


def update_device_coins(token, new_coin_value):
    """Set a device's coin balance to a specific value."""
    db = get_db()
    db.devices.update_one({"top_token": token}, {"$set": {"coin": new_coin_value}})


def increment_device_coins(token, amount):
    """Atomically increment a device's coin balance. Returns new value."""
    db = get_db()
    result = db.devices.find_one_and_update(
        {"top_token": token},
        {"$inc": {"coin": amount}},
        return_document=True,
    )
    return result["coin"] if result else 0


def decrement_device_coins(token, amount):
    """Atomically decrement a device's coin balance. Returns new value."""
    return increment_device_coins(token, -amount)


# ═══════════════════════════════════════════════════════════
#  ACCOUNT OPERATIONS
# ═══════════════════════════════════════════════════════════

def create_account(device_token, account_data):
    """Register an Instagram account under a device token. Returns account doc."""
    db = get_db()

    pk = account_data.get("pk", "")

    # Check if this pk is already registered under this token
    existing = db.accounts.find_one({"device_token": device_token, "pk": pk})
    if existing:
        return existing

    account_id = str(random.randint(100000, 999999))
    # Ensure unique account_id
    while db.accounts.find_one({"account_id": account_id}):
        account_id = str(random.randint(100000, 999999))

    doc = {
        "account_id": account_id,
        "device_token": device_token,
        "pk": pk,
        "username": account_data.get("username", ""),
        "full_name": account_data.get("full_name", ""),
        "profile_pic_url": account_data.get("profile_pic_url", ""),
        "profile_pic_id": account_data.get("profile_pic_id", ""),
        "follower_count": account_data.get("follower_count", "0"),
        "following_count": account_data.get("following_count", "0"),
        "media_count": account_data.get("media_count", "0"),
        "biography": account_data.get("biography", ""),
        "account_type": account_data.get("account_type", ""),
        "is_private": account_data.get("is_private", 0),
        "instagram_agent": account_data.get("instagram_agent", ""),
        "device_id": account_data.get("device_id", ""),
        "collected_coins": 0,
        "created_at": datetime.now(timezone.utc),
    }

    db.accounts.insert_one(doc)
    return doc


def get_account_by_pk(device_token, pk):
    """Look up an account by device token and Instagram pk."""
    db = get_db()
    return db.accounts.find_one({"device_token": device_token, "pk": pk})


def increment_account_collected_coins(account_id, amount):
    """Atomically increment an account's collected coins. Returns new value."""
    db = get_db()
    result = db.accounts.find_one_and_update(
        {"account_id": account_id},
        {"$inc": {"collected_coins": amount}},
        return_document=True,
    )
    return result["collected_coins"] if result else 0


# ═══════════════════════════════════════════════════════════
#  ORDER OPERATIONS
# ═══════════════════════════════════════════════════════════

def create_order(order_type, target_pk, target_username, image_url, order_count, coin_cost, submitted_by_token):
    """Create a new order in the queue. Returns the order document."""
    db = get_db()

    order_id = str(random.randint(100000, 999999))
    # Ensure unique
    while db.orders.find_one({"order_id": order_id}):
        order_id = str(random.randint(100000, 999999))

    doc = {
        "order_id": order_id,
        "order_type": order_type,
        "target_pk": target_pk,
        "target_username": target_username,
        "image_url": image_url or "",
        "order_count": order_count,
        "completed_count": 0,
        "coin_cost": coin_cost,
        "submitted_by_token": submitted_by_token,
        "status": "active",
        "created_at": datetime.now(timezone.utc),
    }

    db.orders.insert_one(doc)
    return doc


def get_random_active_order(exclude_pk=None):
    """Pick a random active order from the queue. Optionally exclude orders targeting a specific pk."""
    db = get_db()

    query = {"status": "active"}
    if exclude_pk:
        query["target_pk"] = {"$ne": exclude_pk}

    # Count active orders
    count = db.orders.count_documents(query)
    if count == 0:
        return None

    # Pick random one
    skip_n = random.randint(0, count - 1)
    cursor = db.orders.find(query).skip(skip_n).limit(1)
    orders = list(cursor)
    return orders[0] if orders else None


def increment_order_completion(order_id):
    """Increment completed_count for an order. Mark as 'completed' if reached order_count."""
    db = get_db()

    order = db.orders.find_one({"order_id": order_id})
    if not order:
        return None

    new_count = order.get("completed_count", 0) + 1
    update = {"$set": {"completed_count": new_count}}

    if new_count >= order.get("order_count", 0):
        update["$set"]["status"] = "completed"

    db.orders.update_one({"order_id": order_id}, update)
    return new_count


def record_order_completion(order_id, account_pk, device_token, reward):
    """Log an individual order completion."""
    db = get_db()
    db.order_completions.insert_one({
        "order_id": order_id,
        "account_pk": account_pk,
        "device_token": device_token,
        "reward": reward,
        "completed_at": datetime.now(timezone.utc),
    })


# ═══════════════════════════════════════════════════════════
#  REQUEST DEDUPLICATION
# ═══════════════════════════════════════════════════════════

def is_request_duplicate(request_id):
    """Check if a request_id has already been processed."""
    db = get_db()
    return db.submitted_requests.find_one({"request_id": request_id}) is not None


def mark_request_processed(request_id):
    """Mark a request_id as processed."""
    db = get_db()
    try:
        db.submitted_requests.insert_one({
            "request_id": request_id,
            "processed_at": datetime.now(timezone.utc),
        })
    except Exception:
        pass  # Duplicate key — already processed
