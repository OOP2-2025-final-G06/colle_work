from datetime import datetime, timedelta

# --- 仮のデータベース ---
SHIFTS_DB = {
    "testuser": {}
}

class ShiftManager:
    def __init__(self, user_name):
        self.user_name = user_name

    # ★変更: debug_date_str を受け取れるように復活
    def get_shift_data(self, debug_date_str=None):
        """
        画面表示に必要なデータを計算して返す
        debug_date_str: テスト用に強制的に日付を変更する場合に使用
        """
        # --- 1. 今日の日付を決定 ---
        if debug_date_str:
            try:
                today = datetime.strptime(debug_date_str, "%Y-%m-%d")
            except ValueError:
                today = datetime.now()
        else:
            today = datetime.now()
        
        # --- 2. 今週と来週の月曜日を計算 ---
        start_of_current_week = today - timedelta(days=today.weekday())
        start_of_next_week = start_of_current_week + timedelta(weeks=1)

        # --- 3. 期間表示用の文字列を作成 ---
        fmt_md = "%m/%d"
        current_end = start_of_current_week + timedelta(days=6)
        next_end = start_of_next_week + timedelta(days=6)

        current_range = f"{start_of_current_week.strftime(fmt_md)} 〜 {current_end.strftime(fmt_md)}"
        next_range = f"{start_of_next_week.strftime(fmt_md)} 〜 {next_end.strftime(fmt_md)}"

        # --- 4. リストデータ作成 ---
        current_week_list = self._create_week_list(start_of_current_week)
        next_week_list = self._create_week_list(start_of_next_week)

        return {
            "user_name": self.user_name,
            "current_date": today.strftime("%Y-%m-%d"),
            "current_range": current_range,
            "next_range": next_range,
            "current_week_shifts": current_week_list,
            "next_week_shifts": next_week_list
        }

    def register_shift(self, date_str, start_time, end_time):
        if self.user_name not in SHIFTS_DB:
            SHIFTS_DB[self.user_name] = {}

        if start_time and end_time:
            fmt = '%H:%M'
            t1 = datetime.strptime(start_time, fmt)
            t2 = datetime.strptime(end_time, fmt)
            
            if t2 < t1:
                t2 += timedelta(days=1)
                
            delta = t2 - t1
            duration = delta.total_seconds() / 3600

            SHIFTS_DB[self.user_name][date_str] = {
                "start": start_time,
                "end": end_time,
                "duration": round(duration, 2)
            }
        
        elif (not start_time or not end_time) and date_str in SHIFTS_DB[self.user_name]:
            del SHIFTS_DB[self.user_name][date_str]

    def _create_week_list(self, start_date):
        week_list = []
        user_shifts = SHIFTS_DB.get(self.user_name, {})

        for i in range(7):
            target_date = start_date + timedelta(days=i)
            date_str = target_date.strftime("%Y-%m-%d")
            
            shift_data = user_shifts.get(date_str, {"start": "", "end": "", "duration": 0})
            
            week_list.append({
                "shift_date": date_str,
                "start_time": shift_data["start"],
                "end_time": shift_data["end"],
                "shift_hour": shift_data["duration"],
                "weekday": target_date.strftime("%a")
            })
        return week_list