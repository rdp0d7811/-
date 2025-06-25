from data_utils import load_data, save_data, update_points
from telebot import TeleBot

def register_referral(bot: TeleBot, user_id: int, ref_id: str, username: str = None):
    data = load_data()

    # تأكد أن المستخدم لا يحاول إحالة نفسه
    if ref_id == str(user_id):
        return False

    # تأكد أن صاحب الرابط موجود
    if str(ref_id) not in data:
        return False

    # تأكد أن المستخدم جديد تماماً
    if str(user_id) in data:
        return False

    # سجل بيانات المستخدم
    data[str(user_id)] = {
        "points": 1,
        "last_daily": 0,
        "progress": 0,
        "referred_by": ref_id,
        "ref_claimed": True
    }

    # أضف نقطة لصاحب الرابط
    data[str(ref_id)]["points"] = data[str(ref_id)].get("points", 0) + 1

    # حفظ التغييرات
    save_data(data)

    # رسالة للمستخدم الجديد
    bot.send_message(user_id, "✅ تم تفعيل البوت بنجاح!\n🎯 تم إضافة محاولة إلى حسابك.")

    # رسالة لصاحب رابط الإحالة
    try:
        username_display = f"@{username}" if username else f"ID: {user_id}"
        bot.send_message(int(ref_id), f"🎉 قام {username_display} بتفعيل البوت من خلال رابطك!\n🎯 تمت إضافة محاولة إلى حسابك.")
    except:
        pass

    return True
