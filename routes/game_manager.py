import sqlite3
import json
from flask import Blueprint, request, jsonify

game_bp = Blueprint('game_api', __name__)

# データベースファイル名
DB_PATH = "game.db"

# データベース初期化（テーブル作成）
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            user_token INTEGER DEFAULT 0,
            stage INTEGER DEFAULT 1,
            stats_json TEXT
        )
    ''')
    # 初期ユーザー(ID:1)がいなければ作成
    c.execute("SELECT count(*) FROM users WHERE id = 1")
    if c.fetchone()[0] == 0:
        default_stats = json.dumps({
            "atk": 3, "atkLevel": 1,
            "critRate": 0.05, "critLevel": 1
        })
        c.execute("INSERT INTO users (id, user_token, stage, stats_json) VALUES (1, 0, 1, ?)", (default_stats,))
        conn.commit()
        print("初期ユーザーを作成しました")
    
    conn.close()

# アプリ起動時にDB初期化を実行
init_db()

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# --- API ---

@game_bp.route('/api/get_data', methods=['GET'])
def get_data():
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE id = 1').fetchone()
    conn.close()

    if user:
        return jsonify({
            "user_token": user['user_token'],
            "stage": user['stage'],
            "stats": json.loads(user['stats_json'])
        })
    else:
        return jsonify({"error": "User not found"}), 404

@game_bp.route('/api/update_data', methods=['POST'])
def update_data():
    new_data = request.json
    stats_str = json.dumps(new_data.get("stats"))
    
    conn = get_db_connection()
    conn.execute('''
        UPDATE users
        SET user_token = ?, stage = ?, stats_json = ?
        WHERE id = 1
    ''', (new_data['user_token'], new_data['stage'], stats_str))
    conn.commit()
    conn.close()
    
    return jsonify({"status": "saved"})