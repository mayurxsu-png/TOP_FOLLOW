"""
Route: Secret Admin Dashboard
  GET  /api/adminu           — Admin dashboard page
  GET  /api/adminu/stats     — JSON stats
  GET  /api/adminu/devices   — List all devices
  GET  /api/adminu/accounts  — List all accounts
  GET  /api/adminu/orders    — List all orders
  DELETE /api/adminu/devices/<token>  — Delete a device
  DELETE /api/adminu/orders/<order_id> — Delete/cancel an order
  POST /api/adminu/devices/<token>/coins — Set coin balance
  POST /api/adminu/orders/seed — Create a seed order for testing
"""

import json
from flask import Blueprint, request, jsonify, render_template_string
from database import get_db
from datetime import datetime, timezone

admin_bp = Blueprint("admin", __name__)


# ═══════════════════════════════════════════════════════════
#  ADMIN DASHBOARD HTML PAGE
# ═══════════════════════════════════════════════════════════

ADMIN_HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TopFollow Admin — Command Center</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }

        :root {
            --bg-primary: #0a0a0f;
            --bg-secondary: #111119;
            --bg-card: #16161f;
            --bg-card-hover: #1c1c28;
            --bg-input: #1a1a26;
            --border: #2a2a3a;
            --border-accent: #3a3a50;
            --text-primary: #e8e8f0;
            --text-secondary: #8888a0;
            --text-muted: #555570;
            --accent-blue: #4f7df7;
            --accent-blue-glow: rgba(79, 125, 247, 0.15);
            --accent-purple: #7c5bf5;
            --accent-purple-glow: rgba(124, 91, 245, 0.15);
            --accent-green: #34d399;
            --accent-green-glow: rgba(52, 211, 153, 0.15);
            --accent-orange: #f59e0b;
            --accent-orange-glow: rgba(245, 158, 11, 0.15);
            --accent-red: #ef4444;
            --accent-red-glow: rgba(239, 68, 68, 0.15);
            --accent-cyan: #22d3ee;
            --gradient-1: linear-gradient(135deg, #4f7df7, #7c5bf5);
            --gradient-2: linear-gradient(135deg, #7c5bf5, #c084fc);
            --shadow-sm: 0 1px 3px rgba(0,0,0,0.3);
            --shadow-md: 0 4px 12px rgba(0,0,0,0.4);
            --shadow-lg: 0 8px 30px rgba(0,0,0,0.5);
            --radius: 12px;
            --radius-sm: 8px;
        }

        body {
            font-family: 'Inter', -apple-system, sans-serif;
            background: var(--bg-primary);
            color: var(--text-primary);
            min-height: 100vh;
            overflow-x: hidden;
        }

        /* ═══ BACKGROUND EFFECTS ═══ */
        body::before {
            content: '';
            position: fixed;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(ellipse at 20% 20%, rgba(79, 125, 247, 0.03) 0%, transparent 60%),
                        radial-gradient(ellipse at 80% 80%, rgba(124, 91, 245, 0.03) 0%, transparent 60%);
            z-index: -1;
            animation: bgShift 20s ease-in-out infinite alternate;
        }

        @keyframes bgShift {
            0% { transform: translate(0, 0); }
            100% { transform: translate(-5%, -5%); }
        }

        /* ═══ TOP NAV ═══ */
        .topnav {
            position: sticky;
            top: 0;
            z-index: 100;
            background: rgba(10, 10, 15, 0.85);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border-bottom: 1px solid var(--border);
            padding: 0 32px;
            height: 64px;
            display: flex;
            align-items: center;
            justify-content: space-between;
        }

        .topnav-brand {
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .topnav-logo {
            width: 36px;
            height: 36px;
            background: var(--gradient-1);
            border-radius: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            font-weight: 800;
            color: #fff;
            box-shadow: 0 0 20px rgba(79, 125, 247, 0.3);
        }

        .topnav-title {
            font-size: 18px;
            font-weight: 700;
            background: var(--gradient-1);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .topnav-badge {
            font-size: 10px;
            padding: 3px 8px;
            border-radius: 20px;
            background: rgba(79, 125, 247, 0.15);
            color: var(--accent-blue);
            font-weight: 600;
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }

        .topnav-right {
            display: flex;
            align-items: center;
            gap: 12px;
        }

        .topnav-status {
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 13px;
            color: var(--text-secondary);
        }

        .status-dot {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: var(--accent-green);
            box-shadow: 0 0 8px var(--accent-green);
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }

        /* ═══ MAIN LAYOUT ═══ */
        .main {
            max-width: 1400px;
            margin: 0 auto;
            padding: 28px 32px;
        }

        /* ═══ STATS GRID ═══ */
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(4, 1fr);
            gap: 16px;
            margin-bottom: 28px;
        }

        .stat-card {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            padding: 22px 24px;
            position: relative;
            overflow: hidden;
            transition: all 0.3s ease;
        }

        .stat-card:hover {
            border-color: var(--border-accent);
            transform: translateY(-2px);
            box-shadow: var(--shadow-md);
        }

        .stat-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 2px;
        }

        .stat-card:nth-child(1)::before { background: var(--gradient-1); }
        .stat-card:nth-child(2)::before { background: linear-gradient(90deg, var(--accent-green), #10b981); }
        .stat-card:nth-child(3)::before { background: linear-gradient(90deg, var(--accent-orange), #f97316); }
        .stat-card:nth-child(4)::before { background: linear-gradient(90deg, var(--accent-purple), #a855f7); }

        .stat-label {
            font-size: 12px;
            font-weight: 500;
            color: var(--text-secondary);
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 8px;
        }

        .stat-value {
            font-size: 32px;
            font-weight: 800;
            font-variant-numeric: tabular-nums;
            line-height: 1.1;
        }

        .stat-card:nth-child(1) .stat-value { color: var(--accent-blue); }
        .stat-card:nth-child(2) .stat-value { color: var(--accent-green); }
        .stat-card:nth-child(3) .stat-value { color: var(--accent-orange); }
        .stat-card:nth-child(4) .stat-value { color: var(--accent-purple); }

        .stat-sub {
            font-size: 12px;
            color: var(--text-muted);
            margin-top: 6px;
        }

        /* ═══ TABS ═══ */
        .tabs {
            display: flex;
            gap: 4px;
            margin-bottom: 20px;
            background: var(--bg-secondary);
            border-radius: var(--radius);
            padding: 4px;
            border: 1px solid var(--border);
        }

        .tab-btn {
            flex: 1;
            padding: 10px 16px;
            border: none;
            background: transparent;
            color: var(--text-secondary);
            font-family: 'Inter', sans-serif;
            font-size: 13px;
            font-weight: 600;
            border-radius: var(--radius-sm);
            cursor: pointer;
            transition: all 0.25s ease;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
        }

        .tab-btn:hover {
            color: var(--text-primary);
            background: rgba(255,255,255,0.03);
        }

        .tab-btn.active {
            background: var(--bg-card);
            color: var(--text-primary);
            box-shadow: var(--shadow-sm);
        }

        .tab-count {
            font-size: 11px;
            padding: 2px 7px;
            border-radius: 10px;
            background: rgba(79, 125, 247, 0.15);
            color: var(--accent-blue);
            font-weight: 600;
        }

        .tab-btn.active .tab-count {
            background: var(--accent-blue);
            color: #fff;
        }

        /* ═══ PANELS ═══ */
        .panel {
            display: none;
            animation: fadeIn 0.3s ease;
        }

        .panel.active { display: block; }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(8px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* ═══ ACTION BAR ═══ */
        .action-bar {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 12px;
            margin-bottom: 16px;
        }

        .search-box {
            flex: 1;
            max-width: 360px;
            position: relative;
        }

        .search-box input {
            width: 100%;
            padding: 10px 14px 10px 38px;
            background: var(--bg-input);
            border: 1px solid var(--border);
            border-radius: var(--radius-sm);
            color: var(--text-primary);
            font-family: 'Inter', sans-serif;
            font-size: 13px;
            outline: none;
            transition: border-color 0.2s;
        }

        .search-box input:focus {
            border-color: var(--accent-blue);
            box-shadow: 0 0 0 3px var(--accent-blue-glow);
        }

        .search-box::before {
            content: '🔍';
            position: absolute;
            left: 12px;
            top: 50%;
            transform: translateY(-50%);
            font-size: 13px;
            pointer-events: none;
        }

        .btn {
            padding: 9px 18px;
            border: none;
            border-radius: var(--radius-sm);
            font-family: 'Inter', sans-serif;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            display: inline-flex;
            align-items: center;
            gap: 6px;
        }

        .btn-primary {
            background: var(--gradient-1);
            color: #fff;
            box-shadow: 0 2px 10px rgba(79, 125, 247, 0.3);
        }
        .btn-primary:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 16px rgba(79, 125, 247, 0.4);
        }

        .btn-danger {
            background: rgba(239, 68, 68, 0.12);
            color: var(--accent-red);
            border: 1px solid rgba(239, 68, 68, 0.2);
        }
        .btn-danger:hover {
            background: rgba(239, 68, 68, 0.2);
        }

        .btn-success {
            background: rgba(52, 211, 153, 0.12);
            color: var(--accent-green);
            border: 1px solid rgba(52, 211, 153, 0.2);
        }
        .btn-success:hover {
            background: rgba(52, 211, 153, 0.2);
        }

        .btn-sm {
            padding: 5px 12px;
            font-size: 12px;
        }

        /* ═══ TABLE ═══ */
        .table-wrapper {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            overflow: hidden;
        }

        table {
            width: 100%;
            border-collapse: collapse;
        }

        thead th {
            padding: 12px 16px;
            text-align: left;
            font-size: 11px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.8px;
            color: var(--text-muted);
            background: rgba(0,0,0,0.2);
            border-bottom: 1px solid var(--border);
            position: sticky;
            top: 0;
        }

        tbody td {
            padding: 12px 16px;
            font-size: 13px;
            border-bottom: 1px solid rgba(255,255,255,0.03);
            vertical-align: middle;
        }

        tbody tr {
            transition: background 0.15s;
        }

        tbody tr:hover {
            background: var(--bg-card-hover);
        }

        .mono {
            font-family: 'JetBrains Mono', monospace;
            font-size: 12px;
            color: var(--accent-cyan);
        }

        .badge {
            display: inline-flex;
            padding: 3px 10px;
            border-radius: 20px;
            font-size: 11px;
            font-weight: 600;
        }

        .badge-active {
            background: var(--accent-green-glow);
            color: var(--accent-green);
        }

        .badge-completed {
            background: var(--accent-blue-glow);
            color: var(--accent-blue);
        }

        .badge-cancelled {
            background: var(--accent-red-glow);
            color: var(--accent-red);
        }

        .badge-follow {
            background: var(--accent-purple-glow);
            color: var(--accent-purple);
        }

        .badge-like {
            background: var(--accent-orange-glow);
            color: var(--accent-orange);
        }

        .coin-display {
            display: inline-flex;
            align-items: center;
            gap: 4px;
            color: var(--accent-orange);
            font-weight: 600;
            font-variant-numeric: tabular-nums;
        }

        /* ═══ MODAL ═══ */
        .modal-overlay {
            display: none;
            position: fixed;
            inset: 0;
            background: rgba(0, 0, 0, 0.7);
            backdrop-filter: blur(8px);
            z-index: 1000;
            align-items: center;
            justify-content: center;
        }

        .modal-overlay.show {
            display: flex;
            animation: fadeIn 0.2s ease;
        }

        .modal {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: var(--radius);
            padding: 28px;
            width: 100%;
            max-width: 480px;
            box-shadow: var(--shadow-lg);
        }

        .modal h3 {
            font-size: 18px;
            font-weight: 700;
            margin-bottom: 20px;
            background: var(--gradient-1);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .form-group {
            margin-bottom: 16px;
        }

        .form-group label {
            display: block;
            font-size: 12px;
            font-weight: 600;
            color: var(--text-secondary);
            margin-bottom: 6px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .form-group input, .form-group select {
            width: 100%;
            padding: 10px 14px;
            background: var(--bg-input);
            border: 1px solid var(--border);
            border-radius: var(--radius-sm);
            color: var(--text-primary);
            font-family: 'Inter', sans-serif;
            font-size: 14px;
            outline: none;
            transition: border-color 0.2s;
        }

        .form-group input:focus, .form-group select:focus {
            border-color: var(--accent-blue);
            box-shadow: 0 0 0 3px var(--accent-blue-glow);
        }

        .modal-actions {
            display: flex;
            gap: 10px;
            justify-content: flex-end;
            margin-top: 24px;
        }

        .btn-ghost {
            padding: 9px 18px;
            border: 1px solid var(--border);
            background: transparent;
            color: var(--text-secondary);
            border-radius: var(--radius-sm);
            font-family: 'Inter', sans-serif;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
        }
        .btn-ghost:hover {
            border-color: var(--border-accent);
            color: var(--text-primary);
        }

        /* ═══ TOAST ═══ */
        .toast-container {
            position: fixed;
            top: 80px;
            right: 24px;
            z-index: 2000;
            display: flex;
            flex-direction: column;
            gap: 8px;
        }

        .toast {
            padding: 12px 20px;
            border-radius: var(--radius-sm);
            font-size: 13px;
            font-weight: 500;
            animation: slideIn 0.3s ease, slideOut 0.3s ease 2.7s forwards;
            box-shadow: var(--shadow-md);
        }

        .toast-success {
            background: rgba(52, 211, 153, 0.15);
            border: 1px solid rgba(52, 211, 153, 0.3);
            color: var(--accent-green);
        }

        .toast-error {
            background: rgba(239, 68, 68, 0.15);
            border: 1px solid rgba(239, 68, 68, 0.3);
            color: var(--accent-red);
        }

        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }

        @keyframes slideOut {
            from { opacity: 1; }
            to { opacity: 0; transform: translateY(-10px); }
        }

        /* ═══ EMPTY STATE ═══ */
        .empty-state {
            text-align: center;
            padding: 60px 20px;
            color: var(--text-muted);
        }

        .empty-state-icon {
            font-size: 48px;
            margin-bottom: 16px;
        }

        .empty-state p {
            font-size: 14px;
            margin-bottom: 20px;
        }

        /* ═══ RESPONSIVE ═══ */
        @media (max-width: 900px) {
            .stats-grid { grid-template-columns: repeat(2, 1fr); }
            .main { padding: 20px 16px; }
            .topnav { padding: 0 16px; }
        }

        @media (max-width: 600px) {
            .stats-grid { grid-template-columns: 1fr; }
            .tabs { flex-wrap: wrap; }
            .action-bar { flex-wrap: wrap; }
            .search-box { max-width: 100%; }
        }

        .loading-spinner {
            display: inline-block;
            width: 16px;
            height: 16px;
            border: 2px solid rgba(255,255,255,0.1);
            border-top-color: var(--accent-blue);
            border-radius: 50%;
            animation: spin 0.6s linear infinite;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <!-- TOP NAV -->
    <nav class="topnav">
        <div class="topnav-brand">
            <div class="topnav-logo">T</div>
            <span class="topnav-title">TopFollow Admin</span>
            <span class="topnav-badge">Secret Panel</span>
        </div>
        <div class="topnav-right">
            <div class="topnav-status">
                <span class="status-dot"></span>
                <span>Server Online</span>
            </div>
            <button class="btn btn-primary btn-sm" onclick="refreshAll()">↻ Refresh</button>
        </div>
    </nav>

    <!-- MAIN CONTENT -->
    <div class="main">
        <!-- STATS -->
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Total Devices</div>
                <div class="stat-value" id="stat-devices">—</div>
                <div class="stat-sub">Registered devices</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Total Accounts</div>
                <div class="stat-value" id="stat-accounts">—</div>
                <div class="stat-sub">Instagram accounts</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Active Orders</div>
                <div class="stat-value" id="stat-orders">—</div>
                <div class="stat-sub">In queue</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Tasks Completed</div>
                <div class="stat-value" id="stat-completions">—</div>
                <div class="stat-sub">Order completions</div>
            </div>
        </div>

        <!-- TABS -->
        <div class="tabs">
            <button class="tab-btn active" onclick="switchTab('devices')">
                📱 Devices <span class="tab-count" id="tab-count-devices">0</span>
            </button>
            <button class="tab-btn" onclick="switchTab('accounts')">
                👤 Accounts <span class="tab-count" id="tab-count-accounts">0</span>
            </button>
            <button class="tab-btn" onclick="switchTab('orders')">
                📋 Orders <span class="tab-count" id="tab-count-orders">0</span>
            </button>
            <button class="tab-btn" onclick="switchTab('completions')">
                ✅ Completions <span class="tab-count" id="tab-count-completions">0</span>
            </button>
        </div>

        <!-- DEVICES PANEL -->
        <div class="panel active" id="panel-devices">
            <div class="action-bar">
                <div class="search-box">
                    <input type="text" placeholder="Search devices by token..." id="search-devices" oninput="filterTable('devices')">
                </div>
            </div>
            <div class="table-wrapper">
                <table>
                    <thead>
                        <tr>
                            <th>Token</th>
                            <th>Device UID</th>
                            <th>Android ID</th>
                            <th>Coins</th>
                            <th>Version</th>
                            <th>Created</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody id="tbody-devices">
                        <tr><td colspan="7" class="empty-state"><div class="loading-spinner"></div></td></tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- ACCOUNTS PANEL -->
        <div class="panel" id="panel-accounts">
            <div class="action-bar">
                <div class="search-box">
                    <input type="text" placeholder="Search by username or pk..." id="search-accounts" oninput="filterTable('accounts')">
                </div>
            </div>
            <div class="table-wrapper">
                <table>
                    <thead>
                        <tr>
                            <th>Account ID</th>
                            <th>Username</th>
                            <th>PK</th>
                            <th>Device Token</th>
                            <th>Collected Coins</th>
                            <th>Created</th>
                        </tr>
                    </thead>
                    <tbody id="tbody-accounts">
                        <tr><td colspan="6" class="empty-state"><div class="loading-spinner"></div></td></tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- ORDERS PANEL -->
        <div class="panel" id="panel-orders">
            <div class="action-bar">
                <div class="search-box">
                    <input type="text" placeholder="Search orders..." id="search-orders" oninput="filterTable('orders')">
                </div>
                <button class="btn btn-primary" onclick="showSeedModal()">+ Seed Order</button>
            </div>
            <div class="table-wrapper">
                <table>
                    <thead>
                        <tr>
                            <th>Order ID</th>
                            <th>Type</th>
                            <th>Target</th>
                            <th>Progress</th>
                            <th>Coin Cost</th>
                            <th>Status</th>
                            <th>Created</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody id="tbody-orders">
                        <tr><td colspan="8" class="empty-state"><div class="loading-spinner"></div></td></tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- COMPLETIONS PANEL -->
        <div class="panel" id="panel-completions">
            <div class="action-bar">
                <div class="search-box">
                    <input type="text" placeholder="Search completions..." id="search-completions" oninput="filterTable('completions')">
                </div>
            </div>
            <div class="table-wrapper">
                <table>
                    <thead>
                        <tr>
                            <th>Order ID</th>
                            <th>Account PK</th>
                            <th>Device Token</th>
                            <th>Reward</th>
                            <th>Completed At</th>
                        </tr>
                    </thead>
                    <tbody id="tbody-completions">
                        <tr><td colspan="5" class="empty-state"><div class="loading-spinner"></div></td></tr>
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <!-- TOAST CONTAINER -->
    <div class="toast-container" id="toast-container"></div>

    <!-- SET COINS MODAL -->
    <div class="modal-overlay" id="modal-coins">
        <div class="modal">
            <h3>💰 Set Coin Balance</h3>
            <div class="form-group">
                <label>Device Token</label>
                <input type="text" id="coins-token" readonly>
            </div>
            <div class="form-group">
                <label>New Coin Balance</label>
                <input type="number" id="coins-value" min="0" value="0">
            </div>
            <div class="modal-actions">
                <button class="btn-ghost" onclick="closeModal('modal-coins')">Cancel</button>
                <button class="btn btn-primary" onclick="submitSetCoins()">Update Coins</button>
            </div>
        </div>
    </div>

    <!-- SEED ORDER MODAL -->
    <div class="modal-overlay" id="modal-seed">
        <div class="modal">
            <h3>📋 Create Seed Order</h3>
            <div class="form-group">
                <label>Order Type</label>
                <select id="seed-type">
                    <option value="follow">Follow</option>
                    <option value="like">Like</option>
                    <option value="comment">Comment</option>
                </select>
            </div>
            <div class="form-group">
                <label>Target Username</label>
                <input type="text" id="seed-username" placeholder="e.g. target_user">
            </div>
            <div class="form-group">
                <label>Target PK</label>
                <input type="text" id="seed-pk" placeholder="e.g. 12345678901">
            </div>
            <div class="form-group">
                <label>Order Count</label>
                <input type="number" id="seed-count" min="1" value="100">
            </div>
            <div class="modal-actions">
                <button class="btn-ghost" onclick="closeModal('modal-seed')">Cancel</button>
                <button class="btn btn-primary" onclick="submitSeedOrder()">Create Order</button>
            </div>
        </div>
    </div>

    <script>
        const BASE = '/api/adminu';

        // ═══ TABS ═══
        function switchTab(name) {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            document.querySelectorAll('.panel').forEach(p => p.classList.remove('active'));
            event.currentTarget.classList.add('active');
            document.getElementById('panel-' + name).classList.add('active');
        }

        // ═══ TOASTS ═══
        function showToast(msg, type = 'success') {
            const container = document.getElementById('toast-container');
            const toast = document.createElement('div');
            toast.className = 'toast toast-' + type;
            toast.textContent = msg;
            container.appendChild(toast);
            setTimeout(() => toast.remove(), 3000);
        }

        // ═══ MODALS ═══
        function showModal(id) { document.getElementById(id).classList.add('show'); }
        function closeModal(id) { document.getElementById(id).classList.remove('show'); }

        function showCoinsModal(token, currentCoins) {
            document.getElementById('coins-token').value = token;
            document.getElementById('coins-value').value = currentCoins;
            showModal('modal-coins');
        }

        function showSeedModal() { showModal('modal-seed'); }

        // ═══ DATA FETCHING ═══
        async function fetchJSON(url, opts = {}) {
            try {
                const resp = await fetch(url, opts);
                return await resp.json();
            } catch (e) {
                showToast('Network error: ' + e.message, 'error');
                return null;
            }
        }

        function truncToken(token) {
            if (!token) return '—';
            return token.substring(0, 10) + '…' + token.substring(token.length - 6);
        }

        function fmtDate(dateStr) {
            if (!dateStr) return '—';
            const d = new Date(dateStr);
            return d.toLocaleString('en-IN', { day: '2-digit', month: 'short', year: '2-digit', hour: '2-digit', minute: '2-digit' });
        }

        // ═══ LOAD STATS ═══
        async function loadStats() {
            const data = await fetchJSON(BASE + '/stats');
            if (!data) return;
            document.getElementById('stat-devices').textContent = data.devices || 0;
            document.getElementById('stat-accounts').textContent = data.accounts || 0;
            document.getElementById('stat-orders').textContent = data.active_orders || 0;
            document.getElementById('stat-completions').textContent = data.completions || 0;
            document.getElementById('tab-count-devices').textContent = data.devices || 0;
            document.getElementById('tab-count-accounts').textContent = data.accounts || 0;
            document.getElementById('tab-count-orders').textContent = data.total_orders || 0;
            document.getElementById('tab-count-completions').textContent = data.completions || 0;
        }

        // ═══ LOAD DEVICES ═══
        async function loadDevices() {
            const data = await fetchJSON(BASE + '/devices');
            if (!data) return;
            const tbody = document.getElementById('tbody-devices');
            if (!data.devices || data.devices.length === 0) {
                tbody.innerHTML = '<tr><td colspan="7"><div class="empty-state"><div class="empty-state-icon">📱</div><p>No devices registered yet</p></div></td></tr>';
                return;
            }
            tbody.innerHTML = data.devices.map(d => `
                <tr data-search="${(d.top_token||'') + ' ' + (d.device_uid||'')}">
                    <td><span class="mono" title="${d.top_token}">${truncToken(d.top_token)}</span></td>
                    <td><span class="mono" title="${d.device_uid}">${truncToken(d.device_uid)}</span></td>
                    <td><span class="mono">${d.android_id || '—'}</span></td>
                    <td><span class="coin-display">🪙 ${(d.coin || 0).toLocaleString()}</span></td>
                    <td>${d.app_version || '—'}</td>
                    <td>${fmtDate(d.created_at)}</td>
                    <td>
                        <button class="btn btn-success btn-sm" onclick="showCoinsModal('${d.top_token}', ${d.coin || 0})">💰 Set Coins</button>
                        <button class="btn btn-danger btn-sm" onclick="deleteDevice('${d.top_token}')">🗑</button>
                    </td>
                </tr>
            `).join('');
        }

        // ═══ LOAD ACCOUNTS ═══
        async function loadAccounts() {
            const data = await fetchJSON(BASE + '/accounts');
            if (!data) return;
            const tbody = document.getElementById('tbody-accounts');
            if (!data.accounts || data.accounts.length === 0) {
                tbody.innerHTML = '<tr><td colspan="6"><div class="empty-state"><div class="empty-state-icon">👤</div><p>No accounts registered yet</p></div></td></tr>';
                return;
            }
            tbody.innerHTML = data.accounts.map(a => `
                <tr data-search="${(a.username||'') + ' ' + (a.pk||'') + ' ' + (a.account_id||'')}">
                    <td><span class="mono">${a.account_id}</span></td>
                    <td><strong>@${a.username || '—'}</strong></td>
                    <td><span class="mono">${a.pk || '—'}</span></td>
                    <td><span class="mono" title="${a.device_token}">${truncToken(a.device_token)}</span></td>
                    <td><span class="coin-display">🪙 ${(a.collected_coins || 0).toLocaleString()}</span></td>
                    <td>${fmtDate(a.created_at)}</td>
                </tr>
            `).join('');
        }

        // ═══ LOAD ORDERS ═══
        async function loadOrders() {
            const data = await fetchJSON(BASE + '/orders');
            if (!data) return;
            const tbody = document.getElementById('tbody-orders');
            if (!data.orders || data.orders.length === 0) {
                tbody.innerHTML = '<tr><td colspan="8"><div class="empty-state"><div class="empty-state-icon">📋</div><p>No orders yet</p><button class="btn btn-primary" onclick="showSeedModal()">+ Create Seed Order</button></div></td></tr>';
                return;
            }
            tbody.innerHTML = data.orders.map(o => {
                const statusClass = o.status === 'active' ? 'badge-active' : o.status === 'completed' ? 'badge-completed' : 'badge-cancelled';
                const typeClass = o.order_type === 'follow' ? 'badge-follow' : 'badge-like';
                const pct = o.order_count > 0 ? Math.round((o.completed_count / o.order_count) * 100) : 0;
                return `
                <tr data-search="${(o.order_id||'') + ' ' + (o.target_username||'') + ' ' + (o.order_type||'')}">
                    <td><span class="mono">#${o.order_id}</span></td>
                    <td><span class="badge ${typeClass}">${o.order_type}</span></td>
                    <td><strong>@${o.target_username || '—'}</strong><br><span class="mono" style="font-size:11px">${o.target_pk || ''}</span></td>
                    <td>${o.completed_count}/${o.order_count} <span style="color:var(--text-muted)">(${pct}%)</span></td>
                    <td><span class="coin-display">🪙 ${(o.coin_cost || 0).toLocaleString()}</span></td>
                    <td><span class="badge ${statusClass}">${o.status}</span></td>
                    <td>${fmtDate(o.created_at)}</td>
                    <td>
                        ${o.status === 'active' ? `<button class="btn btn-danger btn-sm" onclick="cancelOrder('${o.order_id}')">Cancel</button>` : ''}
                    </td>
                </tr>`;
            }).join('');
        }

        // ═══ LOAD COMPLETIONS ═══
        async function loadCompletions() {
            const data = await fetchJSON(BASE + '/completions');
            if (!data) return;
            const tbody = document.getElementById('tbody-completions');
            if (!data.completions || data.completions.length === 0) {
                tbody.innerHTML = '<tr><td colspan="5"><div class="empty-state"><div class="empty-state-icon">✅</div><p>No completions yet</p></div></td></tr>';
                return;
            }
            tbody.innerHTML = data.completions.map(c => `
                <tr data-search="${(c.order_id||'') + ' ' + (c.account_pk||'')}">
                    <td><span class="mono">#${c.order_id}</span></td>
                    <td><span class="mono">${c.account_pk || '—'}</span></td>
                    <td><span class="mono" title="${c.device_token}">${truncToken(c.device_token)}</span></td>
                    <td><span class="coin-display">+${c.reward || 0}</span></td>
                    <td>${fmtDate(c.completed_at)}</td>
                </tr>
            `).join('');
        }

        // ═══ SEARCH FILTER ═══
        function filterTable(tab) {
            const query = document.getElementById('search-' + tab).value.toLowerCase();
            const rows = document.querySelectorAll('#tbody-' + tab + ' tr[data-search]');
            rows.forEach(r => {
                const text = r.getAttribute('data-search').toLowerCase();
                r.style.display = text.includes(query) ? '' : 'none';
            });
        }

        // ═══ ACTIONS ═══
        async function deleteDevice(token) {
            if (!confirm('Delete this device and all its accounts?')) return;
            const res = await fetchJSON(BASE + '/devices/' + token, { method: 'DELETE' });
            if (res && res.status === 'ok') {
                showToast('Device deleted');
                refreshAll();
            } else {
                showToast(res?.message || 'Failed', 'error');
            }
        }

        async function cancelOrder(orderId) {
            if (!confirm('Cancel this order?')) return;
            const res = await fetchJSON(BASE + '/orders/' + orderId, { method: 'DELETE' });
            if (res && res.status === 'ok') {
                showToast('Order cancelled');
                refreshAll();
            } else {
                showToast(res?.message || 'Failed', 'error');
            }
        }

        async function submitSetCoins() {
            const token = document.getElementById('coins-token').value;
            const coins = parseInt(document.getElementById('coins-value').value, 10);
            const res = await fetchJSON(BASE + '/devices/' + token + '/coins', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ coins })
            });
            if (res && res.status === 'ok') {
                showToast('Coins updated to ' + coins.toLocaleString());
                closeModal('modal-coins');
                refreshAll();
            } else {
                showToast(res?.message || 'Failed', 'error');
            }
        }

        async function submitSeedOrder() {
            const payload = {
                order_type: document.getElementById('seed-type').value,
                target_username: document.getElementById('seed-username').value,
                target_pk: document.getElementById('seed-pk').value,
                order_count: parseInt(document.getElementById('seed-count').value, 10),
            };
            if (!payload.target_username || !payload.target_pk) {
                showToast('Username and PK are required', 'error');
                return;
            }
            const res = await fetchJSON(BASE + '/orders/seed', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            if (res && res.status === 'ok') {
                showToast('Seed order #' + res.order_id + ' created');
                closeModal('modal-seed');
                refreshAll();
            } else {
                showToast(res?.message || 'Failed', 'error');
            }
        }

        // ═══ REFRESH ALL ═══
        async function refreshAll() {
            await Promise.all([loadStats(), loadDevices(), loadAccounts(), loadOrders(), loadCompletions()]);
        }

        // ═══ AUTO-REFRESH ═══
        refreshAll();
        setInterval(refreshAll, 15000);
    </script>
</body>
</html>
"""


# ═══════════════════════════════════════════════════════════
#  ADMIN API ROUTES
# ═══════════════════════════════════════════════════════════

@admin_bp.route("/api/adminu", methods=["GET"])
def admin_dashboard():
    """Serve the admin dashboard HTML page."""
    return render_template_string(ADMIN_HTML)


@admin_bp.route("/api/adminu/stats", methods=["GET"])
def admin_stats():
    """Return aggregate stats for the dashboard."""
    db = get_db()
    return jsonify({
        "devices": db.devices.count_documents({}),
        "accounts": db.accounts.count_documents({}),
        "active_orders": db.orders.count_documents({"status": "active"}),
        "total_orders": db.orders.count_documents({}),
        "completed_orders": db.orders.count_documents({"status": "completed"}),
        "completions": db.order_completions.count_documents({}),
        "total_coins_in_circulation": sum(
            d.get("coin", 0) for d in db.devices.find({}, {"coin": 1})
        ),
    })


@admin_bp.route("/api/adminu/devices", methods=["GET"])
def admin_devices():
    """List all registered devices."""
    db = get_db()
    devices = list(db.devices.find({}, {"_id": 0}).sort("created_at", -1).limit(500))
    # Convert datetime objects to ISO strings
    for d in devices:
        if "created_at" in d and hasattr(d["created_at"], "isoformat"):
            d["created_at"] = d["created_at"].isoformat()
    return jsonify({"devices": devices})


@admin_bp.route("/api/adminu/accounts", methods=["GET"])
def admin_accounts():
    """List all registered Instagram accounts."""
    db = get_db()
    accounts = list(db.accounts.find({}, {"_id": 0}).sort("created_at", -1).limit(500))
    for a in accounts:
        if "created_at" in a and hasattr(a["created_at"], "isoformat"):
            a["created_at"] = a["created_at"].isoformat()
    return jsonify({"accounts": accounts})


@admin_bp.route("/api/adminu/orders", methods=["GET"])
def admin_orders():
    """List all orders."""
    db = get_db()
    orders = list(db.orders.find({}, {"_id": 0}).sort("created_at", -1).limit(500))
    for o in orders:
        if "created_at" in o and hasattr(o["created_at"], "isoformat"):
            o["created_at"] = o["created_at"].isoformat()
    return jsonify({"orders": orders})


@admin_bp.route("/api/adminu/completions", methods=["GET"])
def admin_completions():
    """List all order completions."""
    db = get_db()
    completions = list(db.order_completions.find({}, {"_id": 0}).sort("completed_at", -1).limit(500))
    for c in completions:
        if "completed_at" in c and hasattr(c["completed_at"], "isoformat"):
            c["completed_at"] = c["completed_at"].isoformat()
    return jsonify({"completions": completions})


@admin_bp.route("/api/adminu/devices/<token>", methods=["DELETE"])
def admin_delete_device(token):
    """Delete a device and its associated accounts."""
    db = get_db()
    device = db.devices.find_one({"top_token": token})
    if not device:
        return jsonify({"status": "error", "message": "Device not found"}), 404

    # Delete associated accounts
    db.accounts.delete_many({"device_token": token})
    # Delete the device
    db.devices.delete_one({"top_token": token})

    return jsonify({"status": "ok", "message": "Device and associated accounts deleted"})


@admin_bp.route("/api/adminu/devices/<token>/coins", methods=["POST"])
def admin_set_coins(token):
    """Set the coin balance for a device."""
    db = get_db()
    device = db.devices.find_one({"top_token": token})
    if not device:
        return jsonify({"status": "error", "message": "Device not found"}), 404

    data = request.get_json(silent=True) or {}
    coins = data.get("coins", 0)

    db.devices.update_one({"top_token": token}, {"$set": {"coin": int(coins)}})

    return jsonify({"status": "ok", "coin": int(coins)})


@admin_bp.route("/api/adminu/orders/<order_id>", methods=["DELETE"])
def admin_cancel_order(order_id):
    """Cancel an active order."""
    db = get_db()
    order = db.orders.find_one({"order_id": order_id})
    if not order:
        return jsonify({"status": "error", "message": "Order not found"}), 404

    db.orders.update_one({"order_id": order_id}, {"$set": {"status": "cancelled"}})

    return jsonify({"status": "ok", "message": "Order cancelled"})


@admin_bp.route("/api/adminu/orders/seed", methods=["POST"])
def admin_seed_order():
    """Create a seed order directly (for testing — no coin deduction)."""
    from models import create_order

    data = request.get_json(silent=True) or {}
    order_type = data.get("order_type", "follow")
    target_username = data.get("target_username", "")
    target_pk = data.get("target_pk", "")
    order_count = data.get("order_count", 100)
    image_url = data.get("image_url", "")

    if not target_username or not target_pk:
        return jsonify({"status": "error", "message": "target_username and target_pk are required"}), 400

    order = create_order(
        order_type=order_type,
        target_pk=target_pk,
        target_username=target_username,
        image_url=image_url,
        order_count=order_count,
        coin_cost=0,
        submitted_by_token="admin_seed",
    )

    return jsonify({
        "status": "ok",
        "order_id": order["order_id"],
        "message": f"Seed order created: {order_count} {order_type}s for @{target_username}",
    })
