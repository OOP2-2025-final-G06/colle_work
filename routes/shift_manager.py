# shift_manager.py

days = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
weekly_shift_data = {}

# 初期化
for d in days:
    weekly_shift_data[f"{d}_start_h"] = ""
    weekly_shift_data[f"{d}_start_m"] = "" 
    weekly_shift_data[f"{d}_end_h"] = ""
    weekly_shift_data[f"{d}_end_m"] = ""   

def update_weekly_shift(form_data):
    """
    HTMLのフォームから送られてきたデータをすべて上書き保存する関数
    form_data には HTMLの select name="..." で指定した名前でデータが入っています
    """
    for key in weekly_shift_data.keys():
        
        weekly_shift_data[key] = form_data.get(key, "")

def get_weekly_shift():
    """保存されている最新のデータを返す"""
    return weekly_shift_data