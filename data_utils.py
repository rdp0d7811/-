import json
import os
import time
from typing import Dict, Any

DATA_FILE = "users_data.json"

def load_data() -> Dict[str, Any]:
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump({}, f)
        return {}
    
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def save_data(data: Dict[str, Any]):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def reset_user_data() -> Dict[str, Any]:
    return {
        "points": 1,
        "stars": 0,
        "active_round": False,
        "questions": [],
        "last_daily": 0,
        "referred_by": None,
        "ref_claimed": False,
        "ref_count": 0,
        "points_from_refs": 0
    }

def can_use_daily(user_id: str) -> bool:
    data = load_data()
    user_data = data.get(user_id, {})
    last_daily = user_data.get("last_daily", 0)
    return (time.time() - last_daily) >= 86400  # 24 ساعة

def set_daily_time(user_id: str):
    data = load_data()
    if user_id not in data:
        data[user_id] = reset_user_data()
    data[user_id]["last_daily"] = time.time()
    save_data(data)

def update_points(user_id: str, points: int):
    data = load_data()
    if user_id not in data:
        data[user_id] = reset_user_data()
    data[user_id]["points"] = max(0, data[user_id].get("points", 0) + points)
    save_data(data)