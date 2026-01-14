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

def get_weekly_shift(username):
    """(既存関数) 指定ユーザーの直近7日分のシフトを取得"""
    init_db()
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute(
            "SELECT * FROM shifts WHERE username=? ORDER BY date DESC LIMIT 7",
            (username,)
        )
        return [dict(row) for row in cur.fetchall()]

def get_calendar_data(username):
    """Topページ用：今週と来週のシフトデータをカレンダー形式で返す"""
    init_db()
    
    today = datetime.now()
    # 今週の月曜日を計算
    start_of_this_week = today - timedelta(days=today.weekday())
    
    # 2週間分の日付リストを作成
    calendar_data = []
    
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        
        # 14日分（今週7日＋来週7日）ループ
        for i in range(14):
            target_date = start_of_this_week + timedelta(days=i)
            date_str = target_date.strftime("%Y-%m-%d")
            
            # DBから該当日のシフトを取得
            cur = conn.execute(
                "SELECT * FROM shifts WHERE username=? AND date=?",
                (username, date_str)
            )
            row = cur.fetchone()
            
            # 曜日判定（0:月曜...6:日曜）
            is_today = (date_str == today.strftime("%Y-%m-%d"))
            weekday_jp = ['月', '火', '水', '木', '金', '土', '日'][target_date.weekday()]
            
            day_info = {
                "date_display": target_date.strftime("%m/%d"),
                "weekday": weekday_jp,
                "is_today": is_today,
                "shift_time": "－" # デフォルト
            }
            
            if row:
                start = f'{row["start_h"]}:{row["start_m"]}'
                end = f'{row["end_h"]}:{row["end_m"]}'
                day_info["shift_time"] = f"{start} 〜 {end}"
            
            calendar_data.append(day_info)

    # 今週分(前半7つ)と来週分(後半7つ)に分ける
    return {
        "this_week": calendar_data[:7],
        "next_week": calendar_data[7:]
    }

def process_and_save_shift(username, form_data):
    """(既存関数) 変更なし"""
    init_db()
    base_date = datetime.strptime(form_data["base_date"], "%Y-%m-%d")
    days_en = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
    shift_results = [] # 戻り値を変更：時間だけでなく日付も返すようにする

    with sqlite3.connect(DB_PATH) as conn:
        for i, day in enumerate(days_en):
            target_date = (base_date + timedelta(days=i)).strftime("%Y-%m-%d")

            sh = form_data.get(f"{day}_start_h")
            sm = form_data.get(f"{day}_start_m")
            eh = form_data.get(f"{day}_end_h")
            em = form_data.get(f"{day}_end_m")

            if all([sh, sm, eh, em]):
                shift_hour = round(
                    (int(eh) + int(em)/60) - (int(sh) + int(sm)/60), 2
                )
                if shift_hour > 0:
                    conn.execute("""
                        INSERT OR REPLACE INTO shifts
                        (username, date, start_h, start_m, end_h, end_m, shift_hour)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (username, target_date, sh, sm, eh, em, shift_hour))

                    # 日付と時間をセットにしてリストに追加
                    shift_results.append({"date": target_date, "hour": shift_hour})

    return shift_results

def save_shift_and_wage(username, form_data):
    """
    シフト登録と給料計算をまとめて行う。
    """
    # シフト保存（日付と時間のリストが返ってくる）
    shift_results = process_and_save_shift(username, form_data)

    # 勤務時間ごとに給料計算・保存
    for item in shift_results:
        # wage_managerに日付も渡すように修正
        wage_manager.save_wage(username, item["hour"], item["date"])

def get_shift_registration_data(username):
    """(既存関数) シフト登録画面用"""
    init_db()
    today = datetime.now()
    days_until_next_monday = (7 - today.weekday()) % 7
    if days_until_next_monday == 0:
        days_until_next_monday = 7
    next_monday = today + timedelta(days=days_until_next_monday)

    days_info = []
    days_jp = ['月', '火', '水', '木', '金', '土', '日']
    days_en = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']

    for i in range(7):
        target_date = next_monday + timedelta(days=i)
        days_info.append({
            'display': target_date.strftime('%m/%d'),
            'day_jp': days_jp[i],
            'day_en': days_en[i]
        })

    return {
        "username": username,
        "next_monday": next_monday.strftime('%Y-%m-%d'),
        "days_info": days_info,
        "current_shifts": get_weekly_shift(username)
    }

def get_weekly_shift_time_map(username):
    """(既存関数) ユーザー管理画面用"""
    init_db()
    days_en = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
    result = {day: '－' for day in days_en}
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute(
            "SELECT date, start_h, start_m, end_h, end_m FROM shifts WHERE username=?",
            (username,)
        )
        for row in cur.fetchall():
            date_obj = datetime.strptime(row["date"], "%Y-%m-%d")
            weekday = date_obj.weekday()
            start = f'{row["start_h"]}:{row["start_m"].zfill(2)}'
            end = f'{row["end_h"]}:{row["end_m"].zfill(2)}'
            result[days_en[weekday]] = f'{start}〜{end}'
    return result