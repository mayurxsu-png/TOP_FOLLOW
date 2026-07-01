#!/usr/bin/env python3
"""
Test script — Exercises all 6 API endpoints against the local Flask server.
Run this AFTER starting the server with: python app.py

Usage:
    python test_api.py
"""

import sys
import os
if sys.platform == "win32":
    os.system("")
    sys.stdout.reconfigure(encoding="utf-8")

import requests
import json
import uuid
import time
import hashlib

BASE_URL = "http://127.0.0.1:5000"


def test_health():
    print("=" * 60)
    print("TEST: Health Check (GET /)")
    print("=" * 60)
    resp = requests.get(f"{BASE_URL}/")
    print(f"  Status: {resp.status_code}")
    print(f"  Response: {json.dumps(resp.json(), indent=2)}")
    print()
    return resp.json()


def test_setup_device():
    print("=" * 60)
    print("TEST: POST /api835/pre-login/setUpDevice.php")
    print("=" * 60)

    data = (
        f"device_id={uuid.uuid4()}"
        f"&android_id={''.join('abcdef1234567890'[:16])}"
        f"&fcm_token="
        f"&app_version=17"
        f"&app_source=apk"
        f"&language=en"
        f"&aaid={uuid.uuid4()}"
    )
    headers = {
        "accept": "application/json",
        "content-type": "application/x-www-form-urlencoded",
        "user-agent": "okhttp/4.12.0",
    }

    resp = requests.post(f"{BASE_URL}/api835/pre-login/setUpDevice.php", headers=headers, data=data)
    result = resp.json()
    print(f"  Status: {resp.status_code}")
    print(f"  Response: {json.dumps(result, indent=2)}")
    print()
    return result


def test_get_main_info(token):
    print("=" * 60)
    print("TEST: POST /api835/getMainInfo.php")
    print("=" * 60)

    headers = {
        "accept": "application/json",
        "content-type": "application/x-www-form-urlencoded",
        "user-agent": "okhttp/4.12.0",
    }
    data = f"token={token}"

    resp = requests.post(f"{BASE_URL}/api835/getMainInfo.php", headers=headers, data=data)
    result = resp.json()
    print(f"  Status: {resp.status_code}")
    print(f"  Response: {json.dumps(result, indent=2)}")
    print()
    return result


def test_instagram_login(token):
    print("=" * 60)
    print("TEST: POST /api835/account/instagramLogin.php")
    print("=" * 60)

    headers = {
        "accept": "application/json",
        "top-token": token,
        "content-type": "application/json",
        "user-agent": "okhttp/4.12.0",
    }
    account_data = {
        "pk": "99887766554",
        "username": "test_user_99",
        "full_name": "Test User",
        "profile_pic_url": "https://example.com/pic.jpg",
        "profile_pic_id": "",
        "follower_count": "0",
        "following_count": "0",
        "media_count": "0",
        "biography": "",
        "account_type": "",
        "is_private": 0,
        "u_a": "Bearer IGT:2:test",
        "u_a_t": "",
        "mid": "abcdefghijklmnopqrstuv",
        "rur": "CLN",
        "claim": "0",
        "direct_region_hint": "",
        "family_device_id": str(uuid.uuid4()),
        "pigeon_session_id": str(uuid.uuid4()),
        "instagram_agent": "Instagram 428.0.0.47.67 Android",
        "fbid_v2": "",
        "interop_messaging_user_fbid": "",
        "time_line_nav_chain": "FeedFragment:feed_timeline:1:cold_start:0.0::",
        "search_nav_chain": "SearchFragment:explore_popular:2:button:0.0:::",
        "u_w": "5Id3OIr5yA==",
        "device_id": str(uuid.uuid4()),
    }

    resp = requests.post(f"{BASE_URL}/api835/account/instagramLogin.php", headers=headers, json=account_data)
    result = resp.json()
    print(f"  Status: {resp.status_code}")
    print(f"  Response: {json.dumps(result, indent=2)}")
    print()
    return result


def test_remote_control(token, pk, username):
    print("=" * 60)
    print("TEST: POST /api835/account/remoteControl.php")
    print("=" * 60)

    headers = {
        "accept": "application/json",
        "top-token": token,
        "content-type": "application/json",
        "user-agent": "okhttp/4.12.0",
    }
    payload = {
        "token": token,
        "action": "poll",
        "reason": "task_fragment_open",
        "task_service_running": False,
        "task_type": "all",
        "single_tasking": True,
        "local_accounts": [{
            "local_id": 1,
            "pk": pk,
            "username": username,
            "login_type": 0,
            "active": True,
            "logout": False,
            "need_authorization": False,
            "status": 0,
            "has_api_session": True,
            "has_web_session": False,
        }]
    }

    resp = requests.post(f"{BASE_URL}/api835/account/remoteControl.php", headers=headers, json=payload)
    result = resp.json()
    print(f"  Status: {resp.status_code}")
    print(f"  Response: {json.dumps(result, indent=2)}")
    print()
    return result


def test_submit_order(token, username="test_target", pk="12345678901", order_count=100):
    print("=" * 60)
    print("TEST: POST /api835/order/submitOrder.php")
    print("=" * 60)

    timestamp = int(time.time())
    raw = f"{username}|{order_count}|follow|{timestamp}|tF_0rD3r_$tAmP_2024_sEcReT"
    stamp_hash = hashlib.sha256(raw.encode("utf-8")).hexdigest()
    stamp = f"{stamp_hash}_{timestamp}"

    headers = {
        "android-name": "9",
        "play-version-name": "8.3.8",
        "device-language": "RW5nbGlzaA==",
        "user-agent": "TopFollow/8.3.8-Release (Android 9; ASUS_Z01QD)",
        "top-language": "en",
        "device-country": "us",
        "version-code": "17",
        "x-user-country": "us",
        "play-version-code": "17",
        "version-name": "8.3.8-Release",
        "top-token": token,
        "content-type": "application/json",
        "accept-encoding": "gzip",
    }

    payload = {
        "request_id": str(uuid.uuid4()),
        "pk": pk,
        "user_pk": pk,
        "image_url": "https://example.com/profile.jpg",
        "username": username,
        "by": "coin",
        "type": "follow",
        "order_count": order_count,
        "start_count": 0,
        "set_order_stamp": stamp,
    }

    resp = requests.post(f"{BASE_URL}/api835/order/submitOrder.php", headers=headers, json=payload)
    result = resp.json()
    print(f"  Status: {resp.status_code}")
    print(f"  Response: {json.dumps(result, indent=2)}")
    print()
    return result


def test_sync_order(token, pk="99887766554", username="test_user_99"):
    print("=" * 60)
    print("TEST: POST /api835/order/syncOrder.php (get new order)")
    print("=" * 60)

    headers = {
        "active-id": pk,
        "accept": "application/json",
        "play-version-name": "8.3.8",
        "version-code": "17",
        "token": token,
        "play-version-code": "17",
        "version-name": "8.3.8-Release",
        "top-token": token,
        "content-type": "application/x-www-form-urlencoded",
        "user-agent": "okhttp/4.12.0",
    }

    payload = {
        "token": token,
        "active_pk": pk,
        "instagram_pk": pk,
        "username": username,
        "profile_pic": "https://example.com/pic.jpg",
        "order_id": "",
        "type": "",
        "pk": "",
        "order_value": "",
        "x4": "empty",
        "x5": "",
        "x6": "empty",
        "x7": "",
        "get_coin": "false",
        "get_new_order": "true",
        "new_order_type": "follow",
        "is_single_tasking": "true",
    }

    resp = requests.post(f"{BASE_URL}/api835/order/syncOrder.php", headers=headers, data=json.dumps(payload))
    result = resp.json()
    print(f"  Status: {resp.status_code}")
    print(f"  Response: {json.dumps(result, indent=2)}")
    print()
    return result


def test_sync_order_complete(token, order, pk="99887766554", username="test_user_99"):
    print("=" * 60)
    print("TEST: POST /api835/order/syncOrder.php (complete + get next)")
    print("=" * 60)

    headers = {
        "active-id": pk,
        "accept": "application/json",
        "play-version-name": "8.3.8",
        "version-code": "17",
        "token": token,
        "play-version-code": "17",
        "version-name": "8.3.8-Release",
        "top-token": token,
        "content-type": "application/x-www-form-urlencoded",
        "user-agent": "okhttp/4.12.0",
    }

    x5 = json.dumps({
        "friendship_status": {
            "blocking": False, "followed_by": False, "following": True,
            "incoming_request": False, "is_bestie": False, "is_private": False,
            "is_restricted": False, "muting": False, "outgoing_request": False,
        },
        "status": "ok"
    })

    payload = {
        "token": token,
        "active_pk": pk,
        "instagram_pk": pk,
        "username": username,
        "profile_pic": "https://example.com/pic.jpg",
        "order_id": order["order_id"],
        "type": order["order_type"],
        "pk": order["pk"],
        "order_value": order["order_value"],
        "x4": order.get("order_stamp", "empty"),
        "x5": x5,
        "x6": "empty",
        "x7": "",
        "get_coin": "true",
        "get_new_order": "true",
        "new_order_type": "follow",
        "is_single_tasking": "true",
    }

    resp = requests.post(f"{BASE_URL}/api835/order/syncOrder.php", headers=headers, data=json.dumps(payload))
    result = resp.json()
    print(f"  Status: {resp.status_code}")
    print(f"  Response: {json.dumps(result, indent=2)}")
    print()
    return result


def main():
    print("\n🚀 TOP_PROJECT API Test Suite\n")

    # 1. Health check
    test_health()

    # 2. Setup device
    device_result = test_setup_device()
    assert device_result["status"] == "ok", "Device setup failed!"
    token = device_result["top_token"]
    print(f"  ✅ Got token: {token[:16]}...\n")

    # 3. Get main info
    info_result = test_get_main_info(token)
    assert info_result["status"] == "ok", "Get main info failed!"

    # 4. Instagram login
    login_result = test_instagram_login(token)
    assert login_result["status"] == "ok", "Instagram login failed!"
    print(f"  ✅ Account ID: {login_result['account_id']}\n")

    # 5. Remote control
    rc_result = test_remote_control(token, "99887766554", "test_user_99")
    assert rc_result["status"] == "ok", "Remote control failed!"

    # 6. Submit an order (first add coins so we can afford it)
    # Farm some coins first via syncOrder with empty order_id
    print("\n📌 Need to farm coins before submitting order...")
    print("   (Manually adding coins for testing by submitting a small order)\n")

    # Submit a small order to test (will fail if no coins — expected)
    submit_result = test_submit_order(token, "target_user_1", "55555555555", 10)
    print(f"  Submit result: {submit_result['status']} - {submit_result.get('message', '')}\n")

    # 7. Sync order (try to get order — may be empty if none submitted)
    sync_result = test_sync_order(token)
    print(f"  Sync result: {sync_result['status']}")
    if sync_result.get("order"):
        print(f"  ✅ Got order: #{sync_result['order']['order_id']}")

        # 8. Complete the order
        complete_result = test_sync_order_complete(token, sync_result["order"])
        print(f"  Complete result: {complete_result['status']}")
        print(f"  Reward: +{complete_result.get('reward', 0)} coins")
        print(f"  New balance: {complete_result.get('coin', 0)}")
    else:
        print("  ℹ️  No orders in queue (expected — submit one first)")

    print("\n" + "=" * 60)
    print("✅ All endpoint tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
