"""
Routes:
  POST /api835/account/instagramLogin.php  — Register an Instagram account
  POST /api835/account/remoteControl.php   — Poll for remote task assignments
"""

from flask import Blueprint, request, jsonify
from models import create_account, get_device_by_token
from utils.token_utils import validate_token_from_request

account_bp = Blueprint("account", __name__)


@account_bp.route("/api835/account/instagramLogin.php", methods=["POST"])
def instagram_login():
    """
    REQUEST — application/json (header: top-token)
    Body: Full Instagram account object with fields:
        pk, username, full_name, profile_pic_url, profile_pic_id,
        follower_count, following_count, media_count, biography,
        account_type, is_private, u_a, u_a_t, mid, rur, claim,
        direct_region_hint, family_device_id, pigeon_session_id,
        instagram_agent, fbid_v2, interop_messaging_user_fbid,
        time_line_nav_chain, search_nav_chain, u_w, device_id

    RESPONSE — application/json:
        {
            "status": "ok",
            "account_id": "<internal-id>",
            "coin": <device-coin-balance>
        }
    """
    token = request.headers.get("top-token", "")

    if not token:
        return jsonify({
            "status": "error",
            "message": "top-token header is required"
        }), 400

    device = get_device_by_token(token)
    if not device:
        return jsonify({
            "status": "error",
            "message": "Invalid token"
        }), 401

    account_data = request.get_json(silent=True) or {}

    if not account_data.get("pk"):
        return jsonify({
            "status": "error",
            "message": "pk is required"
        }), 400

    account = create_account(token, account_data)

    return jsonify({
        "status": "ok",
        "account_id": account["account_id"],
        "coin": device.get("coin", 0),
    })


@account_bp.route("/api835/account/remoteControl.php", methods=["POST"])
def remote_control():
    """
    REQUEST — application/json (header: top-token)
    Body:
        {
            "token": "<top_token>",
            "action": "poll",
            "reason": "task_fragment_open",
            "task_service_running": false,
            "task_type": "all",
            "single_tasking": true,
            "local_accounts": [
                {
                    "local_id": 1,
                    "pk": "...",
                    "username": "...",
                    "login_type": 0,
                    "active": true,
                    "logout": false,
                    "need_authorization": false,
                    "status": 0,
                    "has_api_session": true,
                    "has_web_session": false
                }
            ]
        }

    RESPONSE — application/json:
        {
            "status": "ok",
            "actions": [],
            "message": ""
        }
    """
    token = request.headers.get("top-token", "")

    if not token:
        return jsonify({
            "status": "error",
            "message": "top-token header is required"
        }), 400

    device = get_device_by_token(token)
    if not device:
        return jsonify({
            "status": "error",
            "message": "Invalid token"
        }), 401

    # In a full implementation, this would return task instructions.
    # For now, we simply acknowledge the poll.
    return jsonify({
        "status": "ok",
        "actions": [],
        "message": "",
    })
