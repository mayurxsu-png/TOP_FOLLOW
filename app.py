"""
TOP_PROJECT — Flask API Server (Vercel Deploy)
Entry point: Registers all route blueprints and starts the server.

Usage:
    python app.py

    Then point your client scripts' BASE_URL to:
        http://127.0.0.1:5000
"""

from flask import Flask, jsonify
from config import FLASK_HOST, FLASK_PORT, FLASK_DEBUG, SECRET_KEY

# Import route blueprints
from routes.device import device_bp
from routes.main_info import main_info_bp
from routes.account import account_bp
from routes.order import order_bp
from routes.admin import admin_bp


def create_app():
    """Application factory."""
    app = Flask(__name__)
    app.config["SECRET_KEY"] = SECRET_KEY

    # ─── REGISTER BLUEPRINTS ───
    app.register_blueprint(device_bp)
    app.register_blueprint(main_info_bp)
    app.register_blueprint(account_bp)
    app.register_blueprint(order_bp)
    app.register_blueprint(admin_bp)

    # ─── HEALTH CHECK ───
    @app.route("/", methods=["GET"])
    def health():
        return "Welcome To TOP FOLLOW"

    # ─── ERROR HANDLERS ───
    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"status": "error", "message": "Endpoint not found"}), 404

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"status": "error", "message": "Internal server error"}), 500

    return app


app = create_app()

if __name__ == "__main__":
    import sys
    import os
    if sys.platform == "win32":
        os.system("")
        sys.stdout.reconfigure(encoding="utf-8")

    print()
    print("╔════════════════════════════════════════════════════════════╗")
    print("║   TOP_PROJECT — Flask API Server                          ║")
    print(f"║   Running on http://{FLASK_HOST}:{FLASK_PORT}                        ║")
    print("║   Press Ctrl+C to stop                                    ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print()
    print("  Endpoints:")
    print("    POST /api835/pre-login/setUpDevice.php")
    print("    POST /api835/getMainInfo.php")
    print("    POST /api835/account/instagramLogin.php")
    print("    POST /api835/account/remoteControl.php")
    print("    POST /api835/order/syncOrder.php")
    print("    POST /api835/order/submitOrder.php")
    print("    GET  /api/adminu  ← SECRET ADMIN PANEL")
    print()

    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG)

