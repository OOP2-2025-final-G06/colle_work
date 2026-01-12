import sqlite3
import json
from flask import Blueprint, request, jsonify, session

game_bp = Blueprint('game_api', __name__)

# データベースファイル名
DB_PATH = "game.db"

# データベース初期化
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    # username を主キー(またはユニークキー)としてテーブルを作成
    # 既存の users テーブルと区別するため 'player_data' というテーブル名に変更推奨ですが
    # ここでは分かりやすく users テーブルを再定義します
    c.execute('''
        CREATE TABLE IF NOT EXISTS player_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            user_token INTEGER DEFAULT 0,
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
    # ログインチェック
    if 'username' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    username = session['username']
    
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM player_data WHERE username = ?', (username,)).fetchone()
    
    # ユーザーデータが存在しない場合（初回プレイ時）は新規作成
    if not user:
        default_stats = json.dumps({
            "atk": 3, "atkLevel": 1,
            "critRate": 0.05, "critLevel": 1
        })
        # 初期データを挿入
        conn.execute(
            "INSERT INTO player_data (username, user_token, stage, stats_json) VALUES (?, ?, ?, ?)",
            (username, 0, 1, default_stats)
        )
        conn.commit()
        # 挿入したデータを再取得
        user = conn.execute('SELECT * FROM player_data WHERE username = ?', (username,)).fetchone()
    
    conn.close()

    return jsonify({
        "user_token": user['user_token'],
        "stage": user['stage'],
        "stats": json.loads(user['stats_json'])
    })

@game_bp.route('/api/update_data', methods=['POST'])
def update_data():
    # ログインチェック
    if 'username' not in session:
        return jsonify({"error": "Unauthorized"}), 401

    username = session['username']
    new_data = request.json
    
    # データの検証（簡易）
    if not new_data:
        return jsonify({"error": "No data provided"}), 400

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