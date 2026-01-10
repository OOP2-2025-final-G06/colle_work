# shift_manager.py
#　シフト管理
import sqlite3
from datetime import datetime, timedelta
from routes import wage_manager

DB_PATH = "database.db"

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS shifts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                date TEXT,
                start_h TEXT,
                start_m TEXT,
                end_h TEXT,
                end_m TEXT,
                shift_hour REAL,
                UNIQUE(username, date)
            )
        """)

def update_weekly_shift(form_data):
def get_shift_registration_data(username):
    """
    シフト登録画面で使用するデータを一括で返す。

    内容:
    - 来週月曜日の日付
    - 月〜日までの表示用情報
    - 既存のシフト情報
    """
    init_db()
    
    # 1. 来週の月曜日を計算
    today = datetime.now()
    days_until_next_monday = (7 - today.weekday()) % 7
    if days_until_next_monday == 0: days_until_next_monday = 7
    next_monday = today + timedelta(days=days_until_next_monday)
    
    # 2. 月曜〜日曜までの日付リストを作成
    days_info = []
    days_jp = ['月', '火', '水', '木', '金', '土', '日']
    days_en = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
    
    for i in range(7):
        target_date = next_monday + timedelta(days=i)
        days_info.append({
            'display': target_date.strftime('%m/%d'), # 01/12 形式
            'day_jp': days_jp[i],
            'day_en': days_en[i]
        })
    
    # 3. 必要な情報をまとめて辞書で返す
    return {
        "username": username,
        "next_monday": next_monday.strftime('%Y-%m-%d'),
        "days_info": days_info,
        "current_shifts": get_weekly_shift(username) # 下の関数を呼び出す
    }
        
def get_weekly_shift(username):
    """
    指定ユーザーの直近7日分のシフトを取得する。
    """
    init_db()
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute(
            "SELECT * FROM shifts WHERE username=? ORDER BY date DESC LIMIT 7",
            (username,)
        )
        return [dict(row) for row in cur.fetchall()]


def process_and_save_shift(username, form_data):
    """
    フォーム入力から勤務時間を計算し、シフトを保存する。

    Returns:
        list[float]: 勤務時間（給料計算用）
    """
    init_db()
    base_date = datetime.strptime(form_data["base_date"], "%Y-%m-%d")
    days_en = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
    shift_hour_results = []

    with sqlite3.connect(DB_PATH) as conn:
        for i, day in enumerate(days_en):
            target_date = (base_date + timedelta(days=i)).strftime("%Y-%m-%d")

            sh = form_data.get(f"{day}_start_h")
            sm = form_data.get(f"{day}_start_m")
            eh = form_data.get(f"{day}_end_h")
            em = form_data.get(f"{day}_end_m")

            # 開始・終了がすべて入力されている日のみ処理
            if all([sh, sm, eh, em]):
                # 時刻を小数時間に変換して勤務時間を算出
                shift_hour = round(
                    (int(eh) + int(em)/60) - (int(sh) + int(sm)/60), 2
                )

                # マイナス・0時間は無効
                if shift_hour > 0:
                    conn.execute("""
                        INSERT OR REPLACE INTO shifts
                        (username, date, start_h, start_m, end_h, end_m, shift_hour)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (username, target_date, sh, sm, eh, em, shift_hour))

                    shift_hour_results.append(shift_hour)

    return shift_hour_results

def save_shift_and_wage(username, form_data):
    """
    シフト登録と給料計算をまとめて行う。

    app.py 側ではこの関数を呼ぶだけ
    """
    # シフト保存
    shift_hour_results = process_and_save_shift(username, form_data)

    # 勤務時間ごとに給料計算・保存
    for shift_hour in shift_hour_results:
            wage_manager.save_wage(username, shift_hour)