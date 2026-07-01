"""
Route: POST /api835/getMainInfo.php
Returns device info, coin balance, and app metadata.
"""

from flask import Blueprint, request, jsonify
from models import get_device_by_token
from config import CURRENT_APP_VERSION, MIN_APP_VERSION

main_info_bp = Blueprint("main_info", __name__)


@main_info_bp.route("/api835/getMainInfo.php", methods=["POST"])
def get_main_info():
    """
    REQUEST — application/x-www-form-urlencoded:
        token=<top_token>

    RESPONSE — application/json:
        {
            "status": "ok",
            "coin": 0,
            "username": "",
            "profile_pic": "",
            "follow_order_count": 0,
            "like_order_count": 0,
            "comment_order_count": 0,
            "app_version": 17,
            "min_version": 10
        }
    """
    token = request.form.get("token", "")

    if not token:
        return jsonify({
            "status": "error",
            "message": "token is required"
        }), 400

    device = get_device_by_token(token)
    if not device:
        return jsonify({
            "status": "error",
            "message": "Invalid token"
        }), 401

    # Count active orders by type (from the database)
    from database import get_db
    db = get_db()
    follow_count = db.orders.count_documents({"order_type": "follow", "status": "active"})
    like_count = db.orders.count_documents({"order_type": "like", "status": "active"})
    comment_count = db.orders.count_documents({"order_type": "comment", "status": "active"})

    return jsonify({
        "status": "ok",
        "coin": device.get("coin", 0),
        "username": "",
        "profile_pic": "",
        "follow_order_count": follow_count,
        "like_order_count": like_count,
        "comment_order_count": comment_count,
        "app_version": CURRENT_APP_VERSION,
        "min_version": MIN_APP_VERSION,
    })
