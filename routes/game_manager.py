import sqlite3
import json
from flask import Blueprint, request, jsonify, session

game_bp = Blueprint('game_api', __name__)

DB_PATH = "game.db"

def init_db():
    """ゲーム用データベースとテーブルの初期化"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # ユーザー名(username)をキーにしてデータを保存するテーブル
    c.execute('''
        CREATE TABLE IF NOT EXISTS player_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            user_token INTEGER DEFAULT 50,
            stage INTEGER DEFAULT 1,
            stats_json TEXT
        )
    ''')
    conn.commit()
    conn.close()

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# --- API ---

@game_bp.route('/api/get_data', methods=['GET'])
def get_data():
    if 'username' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    username = session['username']
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM player_data WHERE username = ?', (username,)).fetchone()
    
    # 初回プレイ時はデータを作成
    if not user:
        default_stats = json.dumps({
            "atk": 3, "atkLevel": 1,
            "critRate": 0.05, "critLevel": 1
        })
        initial_token = 50
        conn.execute(
            "INSERT INTO player_data (username, user_token, stage, stats_json) VALUES (?, ?, ?, ?)",
            (username, initial_token, 1, default_stats)
        )
        conn.commit()
        user = conn.execute('SELECT * FROM player_data WHERE username = ?', (username,)).fetchone()
    
    conn.close()

    return jsonify({
        "user_token": user['user_token'],
        "stage": user['stage'],
        "stats": json.loads(user['stats_json'])
    })

@game_bp.route('/api/update_data', methods=['POST'])
def update_data():
    if 'username' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    username = session['username']
    new_data = request.json
    
    if not new_data:
        return jsonify({"error": "No data"}), 400

    stats_str = json.dumps(new_data.get("stats"))
    
    conn = get_db_connection()
    conn.execute('''
        UPDATE player_data
        SET user_token = ?, stage = ?, stats_json = ?
        WHERE username = ?
    ''', (new_data['user_token'], new_data['stage'], stats_str, username))
    conn.commit()
    conn.close()
    
    return jsonify({"status": "saved"})