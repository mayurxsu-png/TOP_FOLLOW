"""
Route: POST /api835/pre-login/setUpDevice.php
Registers a new device and returns a top_token.
"""

from flask import Blueprint, request, jsonify
from models import create_device

device_bp = Blueprint("device", __name__)


@device_bp.route("/api835/pre-login/setUpDevice.php", methods=["POST"])
def setup_device():
    """
    REQUEST — application/x-www-form-urlencoded:
        device_id=<uuid>
        android_id=<hex16>
        fcm_token=<optional>
        app_version=17
        app_source=apk
        language=en
        aaid=<uuid>

    RESPONSE — application/json:
        {
            "status": "ok",
            "top_token": "<64-char-hex>",
            "coin": 0
        }
    """
    device_uid = request.form.get("device_id", "")
    android_id = request.form.get("android_id", "")
    aaid = request.form.get("aaid", "")
    app_version = request.form.get("app_version", "17")
    app_source = request.form.get("app_source", "apk")
    language = request.form.get("language", "en")
    fcm_token = request.form.get("fcm_token", "")

    if not device_uid:
        return jsonify({
            "status": "error",
            "message": "device_id is required"
        }), 400

    device = create_device(
        device_uid=device_uid,
        android_id=android_id,
        aaid=aaid,
        app_version=app_version,
        app_source=app_source,
        language=language,
        fcm_token=fcm_token,
    )

    return jsonify({
        "status": "ok",
        "top_token": device["top_token"],
        "coin": device.get("coin", 0),
    })
