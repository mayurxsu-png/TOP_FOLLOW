"""
TOP_PROJECT Configuration
All configurable constants for the Flask API server.
"""

import os
from dotenv import load_dotenv

# Load .env file if present
load_dotenv()

# ═══════════════════════════════════════════════════════════
#  MONGODB
# ═══════════════════════════════════════════════════════════
# Replace with your MongoDB Atlas connection string
MONGO_URI = os.environ.get(
    "MONGO_URI",
    "mongodb+srv://mayur:eren@topfollow.pbrrvir.mongodb.net/?appName=topfollow"
)
MONGO_DB_NAME = os.environ.get("MONGO_DB_NAME", "topfollow")

# ═══════════════════════════════════════════════════════════
#  FLASK
# ═══════════════════════════════════════════════════════════
FLASK_HOST = os.environ.get("FLASK_HOST", "0.0.0.0")
FLASK_PORT = int(os.environ.get("FLASK_PORT", 5000))
FLASK_DEBUG = os.environ.get("FLASK_DEBUG", "true").lower() == "true"
SECRET_KEY = os.environ.get("SECRET_KEY", "top_follow_flask_secret_key_change_me")

# ═══════════════════════════════════════════════════════════
#  COIN ECONOMY
# ═══════════════════════════════════════════════════════════
COIN_REWARD_PER_TASK = 8          # Coins earned per syncOrder completion
COIN_COST_PER_FOLLOW = 8          # Coins deducted per follower in an order
COIN_COST_PER_LIKE = 5            # Coins deducted per like in an order
COIN_COST_PER_COMMENT = 10        # Coins deducted per comment in an order
INITIAL_COINS = 0                 # Starting coins for a new device

# ═══════════════════════════════════════════════════════════
#  ORDER STAMP VERIFICATION
# ═══════════════════════════════════════════════════════════
ORDER_STAMP_SECRET = "tF_0rD3r_$tAmP_2024_sEcReT"
STAMP_TIMESTAMP_TOLERANCE_SECONDS = 120   # Allow ±120s clock drift

# ═══════════════════════════════════════════════════════════
#  APP METADATA (returned in getMainInfo)
# ═══════════════════════════════════════════════════════════
CURRENT_APP_VERSION = 17
MIN_APP_VERSION = 10
