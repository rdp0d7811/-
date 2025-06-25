import json

POINTS_FILE = "points.json"

def reset_ref_claims():
    try:
        with open(POINTS_FILE, "r") as f:
            data = json.load(f)
    except:
        data = {}

    for user_id in data:
        data[user_id]["ref_claimed"] = False  # ✅ إعادة تفعيل

    with open(POINTS_FILE, "w") as f:
        json.dump(data, f, indent=4)

    print("✅ تم إعادة تفعيل الإحالات لجميع المستخدمين.")

if __name__ == "__main__":
    reset_ref_claims()
