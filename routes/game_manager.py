import sqlite3
import json
from flask import Blueprint, request, jsonify

game_bp = Blueprint('game_api', __name__)

DB_PATH = "user_data.db"

def init_db():
    """ゲーム用データベースとテーブルの初期化"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
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

def get_user_token_from_db(username):
    """DBから現在のトークン数を取得する"""
    init_db() # 念の為初期化
    conn = get_db_connection()
    user = conn.execute('SELECT user_token FROM player_data WHERE username = ?', (username,)).fetchone()
    conn.close()
    
    if user:
        return user['user_token']
    return 0

def add_user_token_to_db(username, amount):
    """DBのトークンを加算する（マイナスなら減る）"""
    init_db()
    conn = get_db_connection()
    
    # ユーザーがいるか確認
    user = conn.execute('SELECT * FROM player_data WHERE username = ?', (username,)).fetchone()
    
    if user:
        # 既存ユーザーなら更新
        new_token = user['user_token'] + amount
        conn.execute('UPDATE player_data SET user_token = ? WHERE username = ?', (new_token, username))
    else:
        # 新規ユーザーなら作成（初期ステータスもセット）
        default_stats = json.dumps({
            "atk": 3, "atkLevel": 1,
            "critRate": 0.05, "critLevel": 1
        })
        # 初期値 + 今回の獲得分
        conn.execute(
            "INSERT INTO player_data (username, user_token, stage, stats_json) VALUES (?, ?, ?, ?)",
            (username, amount, 1, default_stats)
        )
    
    conn.commit()
    conn.close()

# API (ゲーム画面との通信用)

@game_bp.route('/api/get_data', methods=['GET'])
def get_data():
    # URLパラメータからusernameを取得します
    # 例: /api/get_data?username=Player1
    username = request.args.get('username')

    if not username:
        return jsonify({"error": "Username is required"}), 400
    
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM player_data WHERE username = ?', (username,)).fetchone()
    
    # 初回プレイ時はデータを作成
    if not user:
        default_stats = json.dumps({
            "atk": 3, "atkLevel": 1,
            "critRate": 0.05, "critLevel": 1
        })
        initial_token = 0 # 初期トークン
        conn.execute(
            "INSERT INTO player_data (username, user_token, stage, stats_json) VALUES (?, ?, ?, ?)",
            (username, initial_token, 1, default_stats)
        )
        conn.commit()
        user = conn.execute('SELECT * FROM player_data WHERE username = ?', (username,)).fetchone()
    
    conn.close()

    return jsonify({
        "username": user['username'], # 確認用にusernameも返却
        "user_token": user['user_token'],
        "stage": user['stage'],
        "stats": json.loads(user['stats_json'])
    })

@game_bp.route('/api/update_data', methods=['POST'])
def update_data():
    # POSTデータそのものを受け取ります
    new_data = request.json
    
    if not new_data:
        return jsonify({"error": "No data"}), 400

    # JSONデータ内にusernameが含まれていることを期待します
    username = new_data.get('username')

    if not username:
        return jsonify({"error": "Username is required in JSON body"}), 400

    stats_str = json.dumps(new_data.get("stats"))
    
    conn = get_db_connection()
    conn.execute('''
        UPDATE player_data
        SET user_token = ?, stage = ?, stats_json = ?
        WHERE username = ?
    ''', (new_data['user_token'], new_data['stage'], stats_str, username))
    conn.commit()
    conn.close()
    
    return jsonify({"status": "saved", "username": username})