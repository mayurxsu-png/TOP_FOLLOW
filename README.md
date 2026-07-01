# TOP_PROJECT — TopFollow Clone API

A Flask API server that replicates the TopFollow API endpoints, backed by MongoDB Atlas.

## Quick Start

### 1. Install dependencies
```bash
cd TOP_PROJECT
pip install -r requirements.txt
```

### 2. Configure MongoDB
Copy `.env.example` to `.env` and set your MongoDB Atlas URI:
```bash
copy .env.example .env
```
Edit `.env` and replace `<username>`, `<password>`, `<cluster>` with your Atlas credentials.

### 3. Run the server
```bash
python app.py
```
Server starts at `http://127.0.0.1:5000`

### 4. Point your scripts
In your client scripts, change:
```python
BASE_URL = "http://127.0.0.1:5000"
```

---

## API Endpoints

| Endpoint | Method | Content-Type | Description |
|----------|--------|-------------|-------------|
| `/api835/pre-login/setUpDevice.php` | POST | form-urlencoded | Register device, get token |
| `/api835/getMainInfo.php` | POST | form-urlencoded | Get coin balance & info |
| `/api835/account/instagramLogin.php` | POST | JSON | Register Instagram account |
| `/api835/account/remoteControl.php` | POST | JSON | Poll for task assignments |
| `/api835/order/syncOrder.php` | POST | JSON string | Complete task & get next order |
| `/api835/order/submitOrder.php` | POST | JSON | Submit new follow order |

---

## Project Structure

```
TOP_PROJECT/
├── app.py                  # Flask entry point
├── config.py               # All configuration constants
├── database.py             # MongoDB connection singleton
├── models.py               # Data operations (CRUD)
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variable template
├── routes/
│   ├── __init__.py
│   ├── device.py           # setUpDevice endpoint
│   ├── main_info.py        # getMainInfo endpoint
│   ├── account.py          # instagramLogin & remoteControl
│   └── order.py            # syncOrder & submitOrder
└── utils/
    ├── __init__.py
    ├── token_utils.py      # Token generation/validation
    └── stamp_utils.py      # Order stamp SHA-256 verification
```

---

## MongoDB Collections

- **devices** — Registered devices with tokens and coin balances
- **accounts** — Instagram accounts linked to device tokens
- **orders** — Follow/like/comment order queue
- **order_completions** — Log of completed tasks
- **submitted_requests** — Request ID deduplication

---

## Coin Economy

| Action | Coins |
|--------|-------|
| Complete a follow task | +8 |
| Submit 100-follower order | -800 |
| Complete a like task | +8 |
| Submit 100-like order | -500 |
