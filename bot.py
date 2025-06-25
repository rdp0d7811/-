import telebot
import random
import threading
import logging
import time
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from data_utils import (
    load_data,
    save_data,
    can_use_daily,
    update_points,
    set_daily_time,
    reset_user_data
)
from questions import questions
# وفي دالة send_question:
user_data["questions"] = get_random_questions(5)  # بدلاً من random.sample
from subscription_check import get_not_joined_channels, channels

# تهيئة logging
logging.basicConfig(level=logging.DEBUG)

# تعريف البوت
API_TOKEN = '7815627391:AAF206NJX2_XTmXb1qEHi0sIuz6g7NbQRas'
bot = telebot.TeleBot(API_TOKEN)
timers = {}  # قاموس لحفظ المؤقتات

# تعريف دالة إنشاء القائمة الرئيسية
def generate_main_menu(user_id):
    data = load_data()
    user_data = data.get(str(user_id), reset_user_data())
    
    markup = InlineKeyboardMarkup(row_width=2)
    
    # الصف الأول: الأزرار الرئيسية
    markup.row(
        InlineKeyboardButton(f"🎮 لعب جولة ({user_data.get('points', 0)} محاولة)", callback_data="play_round"),
        InlineKeyboardButton(f"⭐ نجومي ({user_data.get('stars', 0)})", callback_data="my_stars")
    )
    
    # الصف الثاني: المكافآت اليومية والإحالات
    markup.row(
        InlineKeyboardButton("🎁 المحاولة اليومية", callback_data="daily_try"),
        InlineKeyboardButton("🔗 تجميع المحاولات", callback_data="referral")
    )
    
    # الصف الثالث: المعلومات والمساعدة
    markup.add(InlineKeyboardButton("ℹ️ كيف أستخدم البوت", callback_data="how_to_use"))
    
    return markup

# تعريف الدوال الأساسية
@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id
    args = message.text.split()
    data = load_data()
    is_new = str(user_id) not in data

    # تحقق الاشتراك بالقنوات أولاً
    not_joined = get_not_joined_channels(bot, user_id)

    if not_joined:
        channel = not_joined[0]
        text = f"🔔 يجب عليك الانضمام إلى القناة التالية 🔔\n\n{channel['name']}\n\n🌟 اضغط على الرابط للانضمام:\n{channel['link']}"
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("✔️ تحقق", callback_data="check_subscription"))
        bot.send_message(user_id, text, reply_markup=keyboard)
        return

    # إذا مشترك في كل القنوات
    if is_new:
        data[str(user_id)] = reset_user_data()

    user_data = data[str(user_id)]

    # معالجة الإحالة إن وجدت
    if len(args) > 1 and args[1].startswith("ref") and is_new:
        ref_id = args[1][3:]
        if ref_id != str(user_id):
            user_data["referred_by"] = ref_id
            user_data["points"] += 1
            if ref_id in data:
                data[ref_id]["points"] += 1
                data[ref_id]["ref_count"] += 1
                data[ref_id]["points_from_refs"] += 1
                try:
                    username = f"@{message.from_user.username}" if message.from_user.username else f"ID: {user_id}"
                    bot.send_message(int(ref_id), f"🎉 قام {username} بتفعيل البوت من خلال رابطك!\n🎯 تم إضافة محاولة إلى حسابك.")
                except:
                    pass

    save_data(data)
    bot.send_message(user_id, f"✅ تم تفعيل البوت بنجاح!\n🎯 عدد محاولاتك الحالي: {user_data['points']}",
                    reply_markup=generate_main_menu(user_id))

# دوال معالجة الأزرار
@bot.callback_query_handler(func=lambda call: call.data == "check_subscription")
def check_subscription(call):
    user_id = call.from_user.id
    not_joined = get_not_joined_channels(bot, user_id)

    if not_joined:
        channel = not_joined[0]
        text = f"🔔 يجب عليك الانضمام إلى القناة التالية 🔔\n\n{channel['name']}\n\n🌟 اضغط على الرابط للانضمام:\n{channel['link']}"
        keyboard = InlineKeyboardMarkup()
        keyboard.add(InlineKeyboardButton("✔️ تحقق", callback_data="check_subscription"))
        bot.send_message(user_id, text, reply_markup=keyboard)
        bot.answer_callback_query(call.id, "🚫 لم يتم الاشتراك بعد.", show_alert=True)
    else:
        bot.answer_callback_query(call.id, "✅ تم التحقق من جميع القنوات!", show_alert=True)
        bot.send_message(user_id, "✅ تم التحقق بنجاح! اكتب أو اضغط على /start للمتابعة.")

@bot.callback_query_handler(func=lambda call: call.data == "how_to_use")
def how_to_use_handler(call):
    bot.answer_callback_query(call.id)
    bot.send_message(call.from_user.id, "👋 مرحباً! إليك كيفية استخدام البوت:\n\n1. اضغط '🎮 لعب جولة' للبدء\n2. لديك 4 ثوانٍ للإجابة\n3. كل إجابة صحيحة تعطيك نجمة\n4. يمكنك الحصول على محاولات يومية")

@bot.callback_query_handler(func=lambda call: call.data == "daily_try")
def handle_daily_try(call):
    user_id = str(call.from_user.id)
    
    if not can_use_daily(user_id):
        bot.answer_callback_query(call.id, "⏳ لقد استخدمت محاولتك اليومية بالفعل!", show_alert=True)
        return
    
    update_points(user_id, 1)
    set_daily_time(user_id)
    
    data = load_data()
    new_points = data[user_id]["points"]
    
    bot.answer_callback_query(call.id, f"🎉 تم منحك محاولة جديدة! (الإجمالي: {new_points})", show_alert=True)
    
    try:
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"👋 مرحباً بك في بوت OnSide Sport!\n\n🎯 عدد محاولاتك الحالي: {new_points}\n⭐ عدد نجومك: {data[user_id].get('stars', 0)}\n\n👇 اختر من الأزرار أدناه:",
            reply_markup=generate_main_menu(user_id)
        )
    except Exception as e:
        print(f"Error updating message: {e}")

@bot.callback_query_handler(func=lambda call: call.data == "play_round")
def play_round(call):
    user_id = str(call.from_user.id)
    data = load_data()
    
    if data[user_id]["points"] <= 0:
        bot.answer_callback_query(call.id, "ليس لديك محاولات كافية!")
        return
    
    data[user_id]["points"] -= 1
    data[user_id]["active_round"] = True
    save_data(data)
    send_question(user_id, 0)
    bot.answer_callback_query(call.id)

def send_question(user_id, q_index):
    try:
        data = load_data()
        user_data = data[str(user_id)]
        
        if not user_data.get("questions"):
            user_data["questions"] = random.sample(questions, min(5, len(questions)))
            save_data(data)
        
        question = user_data["questions"][q_index]
        markup = InlineKeyboardMarkup()
        
        for i, option in enumerate(question["options"]):
            markup.add(InlineKeyboardButton(option, callback_data=f"answer_{q_index}_{i}"))
        
        msg = bot.send_message(
            user_id,
            f"⚽ السؤال ({q_index+1}/{len(user_data['questions'])}):\n\n{question['text']}\n\n⏱ لديك 4 ثوانٍ للإجابة!",
            reply_markup=markup
        )
        
        timer = threading.Timer(4.0, timeout, args=[user_id, msg.message_id, q_index])
        timers[f"{user_id}_{msg.message_id}"] = timer
        timer.start()
        
    except Exception as e:
        print(f"Error in send_question: {e}")
        bot.send_message(user_id, "❌ حدث خطأ في تحميل السؤال")

@bot.callback_query_handler(func=lambda call: call.data.startswith("answer_"))
def handle_answer(call):
    user_id = str(call.from_user.id)
    data = load_data()
    user_data = data[user_id]
    
    # إلغاء المؤقت
    timer_key = f"{user_id}_{call.message.message_id}"
    if timer_key in timers:
        timers[timer_key].cancel()
        del timers[timer_key]
    
    _, q_index, a_index = call.data.split("_")
    q_index, a_index = int(q_index), int(a_index)
    question = user_data["questions"][q_index]
    
    if a_index == question["correct"]:
        user_data["stars"] += 1
        bot.answer_callback_query(call.id, "✅ صحيح! حصلت على ⭐")
        
        try:
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=f"✅ إجابة صحيحة!\n\n{question['text']}\n\nالجواب الصحيح: {question['options'][question['correct']]}\n\nلقد حصلت على ⭐ (الإجمالي: {user_data['stars']})"
            )
        except:
            pass
        
        if q_index + 1 < len(user_data["questions"]):
            threading.Timer(1.5, send_question, args=[user_id, q_index + 1]).start()
        else:
            user_data["active_round"] = False
            bot.send_message(user_id, f"🎉 أكملت جميع الأسئلة!\nإجمالي نجومك: {user_data['stars']}")
    else:
        user_data["active_round"] = False
        bot.answer_callback_query(call.id, "❌ خاطئ!")
        
        try:
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text=f"❌ إجابة خاطئة!\n\n{question['text']}\n\nالجواب الصحيح: {question['options'][question['correct']]}"
            )
        except:
            pass
        
        bot.send_message(user_id, "❌ انتهت الجولة!")
    
    save_data(data)

def timeout(user_id, msg_id, q_index):
    try:
        data = load_data()
        user_data = data[str(user_id)]
        
        if user_data.get("active_round", False):
            question = user_data["questions"][q_index]
            bot.edit_message_text(
                chat_id=user_id,
                message_id=msg_id,
                text=f"⏰ انتهى الوقت!\n\n{question['text']}\n\nالجواب الصحيح: {question['options'][question['correct']]}"
            )
            user_data["active_round"] = False
            save_data(data)
            bot.send_message(user_id, "❌ انتهت الجولة بسبب انتهاء الوقت!")
    except Exception as e:
        print(f"Error in timeout: {e}")
    finally:
        timer_key = f"{user_id}_{msg_id}"
        if timer_key in timers:
            del timers[timer_key]

if __name__ == "__main__":
    print("✅ البوت يعمل الآن!")
    bot.infinity_polling()