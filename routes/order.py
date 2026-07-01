"""
Routes:
  POST /api835/order/syncOrder.php    — Complete an order task & get next order
  POST /api835/order/submitOrder.php  — Submit a new follow/like/comment order
"""

import json
import time
from flask import Blueprint, request, jsonify
from models import (
    get_device_by_token,
    increment_device_coins,
    decrement_device_coins,
    get_account_by_pk,
    increment_account_collected_coins,
    get_random_active_order,
    increment_order_completion,
    record_order_completion,
    create_order,
    is_request_duplicate,
    mark_request_processed,
)
from utils.stamp_utils import verify_order_stamp, generate_order_stamp
from config import (
    COIN_REWARD_PER_TASK,
    COIN_COST_PER_FOLLOW,
    COIN_COST_PER_LIKE,
    COIN_COST_PER_COMMENT,
)

order_bp = Blueprint("order", __name__)


def _format_order_for_response(order_doc):
    """Convert an internal order document to the response format expected by clients."""
    if not order_doc:
        return None

    return {
        "order_id": order_doc["order_id"],
        "order_type": order_doc["order_type"],
        "pk": order_doc["target_pk"],
        "username": order_doc["target_username"],
        "image_url": order_doc.get("image_url", ""),
        "order_value": order_doc["order_type"],  # typically same as order_type
        "order_stamp": generate_order_stamp(
            order_doc["target_username"],
            order_doc["order_count"],
            order_doc["order_type"],
        ),
        "delay": 7,
    }


@order_bp.route("/api835/order/syncOrder.php", methods=["POST"])
def sync_order():
    """
    REQUEST — Content-Type: application/x-www-form-urlencoded (but body is JSON string)
    Headers: active-id, token, top-token, version-code, version-name, play-version-name, play-version-code

    Body (JSON string):
        {
            "token": "<top_token>",
            "active_pk": "...",
            "instagram_pk": "...",
            "username": "...",
            "profile_pic": "...",
            "order_id": "",          // empty on first call
            "type": "",              // empty on first call
            "pk": "",                // empty on first call
            "order_value": "",
            "x4": "empty",
            "x5": "",
            "x6": "empty",
            "x7": "",
            "get_coin": "true",
            "get_new_order": "true",
            "new_order_type": "follow",
            "is_single_tasking": "true"
        }

    RESPONSE — application/json:
        Success with new order:
        {
            "status": "ok",
            "reward": 8,
            "coin": 808,
            "collected_coins": 808,
            "order": {
                "order_id": "123456",
                "order_type": "follow",
                "pk": "98765432101",
                "username": "target_user",
                "image_url": "https://...",
                "order_value": "follow",
                "order_stamp": "<stamp>",
                "delay": 7
            }
        }

        Success without new order:
        {
            "status": "ok",
            "reward": 8,
            "coin": 808,
            "collected_coins": 808,
            "order": null
        }
    """
    # The client sends Content-Type: x-www-form-urlencoded but the body is a JSON string
    # Try to parse as JSON first, then fallback to form data
    payload = None

    try:
        raw_data = request.get_data(as_text=True)
        if raw_data:
            payload = json.loads(raw_data)
    except (json.JSONDecodeError, Exception):
        pass

    if payload is None:
        payload = request.form.to_dict()

    if not payload:
        return jsonify({"status": "error", "message": "Empty request body"}), 400

    # Extract token from header or body
    token = request.headers.get("top-token", "") or payload.get("token", "")

    if not token:
        return jsonify({"status": "error", "message": "Token is required"}), 400

    device = get_device_by_token(token)
    if not device:
        return jsonify({"status": "error", "message": "Invalid token"}), 401

    active_pk = payload.get("active_pk", "") or payload.get("instagram_pk", "")
    username = payload.get("username", "")
    order_id = payload.get("order_id", "")
    order_type = payload.get("type", "")
    get_coin = payload.get("get_coin", "true")
    get_new_order = payload.get("get_new_order", "true")
    new_order_type = payload.get("new_order_type", "follow")

    reward = 0
    new_coin_balance = device.get("coin", 0)
    collected_coins = 0

    # ─── PROCESS COMPLETED ORDER ───
    if order_id and order_type:
        # Extract verification data (x5)
        x5_str = payload.get("x5", "")
        if not x5_str or x5_str == "empty":
            return jsonify({"status": "error", "message": "Verification data (x5) is missing"}), 400

        try:
            x5_data = json.loads(x5_str)
        except Exception:
            return jsonify({"status": "error", "message": "Invalid verification data (x5) format"}), 400

        # Verify action against Instagram response signature
        verified = False
        if order_type == "follow":
            status = x5_data.get("status", "")
            friendship = x5_data.get("friendship_status", {})
            if status == "ok" and (friendship.get("following") is True or friendship.get("outgoing_request") is True):
                verified = True
        elif order_type == "like":
            if x5_data.get("status") == "ok":
                verified = True
        else:
            # Fallback verification
            if x5_data.get("status") == "ok":
                verified = True

        if not verified:
            return jsonify({"status": "error", "message": "Action verification failed (friendship not established)"}), 400

        # This is a completed task — award coins
        reward = COIN_REWARD_PER_TASK

        if get_coin == "true":
            new_coin_balance = increment_device_coins(token, reward)

        # Increment order completion count
        increment_order_completion(order_id)

        # Record the completion
        record_order_completion(order_id, active_pk, token, reward)

        # Update account collected coins
        account = get_account_by_pk(token, active_pk)
        if account:
            collected_coins = increment_account_collected_coins(account["account_id"], reward)
        else:
            collected_coins = reward

    # ─── GET NEW ORDER ───
    next_order = None
    if get_new_order == "true":
        order_doc = get_random_active_order(exclude_pk=active_pk)
        next_order = _format_order_for_response(order_doc)

    return jsonify({
        "status": "ok",
        "reward": reward,
        "coin": new_coin_balance,
        "collected_coins": collected_coins,
        "order": next_order,
    })


@order_bp.route("/api835/order/submitOrder.php", methods=["POST"])
def submit_order():
    """
    REQUEST — application/json (header: top-token)
    Headers: android-name, play-version-name, device-language, top-language,
             device-country, version-code, x-user-country, play-version-code,
             version-name, top-token

    Body:
        {
            "request_id": "<uuid>",
            "pk": "35943425355",
            "user_pk": "35943425355",
            "image_url": "https://...",
            "username": "rajuk.678",
            "by": "coin",
            "type": "follow",
            "order_count": 100,
            "start_count": 0,
            "set_order_stamp": "<sha256>_<timestamp>"
        }

    RESPONSE — application/json:
        Success:
        {
            "status": "ok",
            "order_id": "789012",
            "coin": 708,
            "message": "Order submitted successfully"
        }

        Failure:
        {
            "status": "error",
            "message": "Insufficient coins"
        }
    """
    token = request.headers.get("top-token", "")

    if not token:
        return jsonify({"status": "error", "message": "top-token header is required"}), 400

    device = get_device_by_token(token)
    if not device:
        return jsonify({"status": "error", "message": "Invalid token"}), 401

    payload = request.get_json(silent=True) or {}

    request_id = payload.get("request_id", "")
    target_pk = payload.get("pk", "") or payload.get("user_pk", "")
    username = payload.get("username", "")
    image_url = payload.get("image_url", "")
    order_type = payload.get("type", "follow")
    order_count = payload.get("order_count", 0)
    set_order_stamp = payload.get("set_order_stamp", "")

    # ─── VALIDATION ───

    if not username:
        return jsonify({"status": "error", "message": "username is required"}), 400

    if not order_count or order_count <= 0:
        return jsonify({"status": "error", "message": "order_count must be > 0"}), 400

    if not target_pk:
        return jsonify({"status": "error", "message": "pk is required"}), 400

    # ─── REQUEST DEDUPLICATION ───
    if request_id and is_request_duplicate(request_id):
        return jsonify({"status": "error", "message": "Duplicate request"}), 409

    # ─── STAMP VERIFICATION ───
    if not verify_order_stamp(set_order_stamp, username, order_count, order_type):
        return jsonify({"status": "error", "message": "Invalid order stamp"}), 403

    # ─── CALCULATE COIN COST ───
    cost_map = {
        "follow": COIN_COST_PER_FOLLOW,
        "like": COIN_COST_PER_LIKE,
        "comment": COIN_COST_PER_COMMENT,
    }
    per_unit_cost = cost_map.get(order_type, COIN_COST_PER_FOLLOW)
    total_cost = order_count * per_unit_cost

    # ─── CHECK BALANCE ───
    current_coins = device.get("coin", 0)
    if current_coins < total_cost:
        return jsonify({
            "status": "error",
            "message": f"Insufficient coins. Need {total_cost}, have {current_coins}"
        }), 400

    # ─── DEDUCT COINS ───
    new_balance = decrement_device_coins(token, total_cost)

    # ─── CREATE ORDER ───
    order = create_order(
        order_type=order_type,
        target_pk=target_pk,
        target_username=username,
        image_url=image_url,
        order_count=order_count,
        coin_cost=total_cost,
        submitted_by_token=token,
    )

    # ─── MARK REQUEST PROCESSED ───
    if request_id:
        mark_request_processed(request_id)

    return jsonify({
        "status": "ok",
        "order_id": order["order_id"],
        "coin": new_balance,
        "message": "Order submitted successfully",
    })
