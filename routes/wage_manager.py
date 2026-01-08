# wage_manager.py

# 時給（初期値）
_salary_per_hour = 1000


def get_salary():
    return _salary_per_hour


def set_salary(value: int):
    global _salary_per_hour
    _salary_per_hour = value
