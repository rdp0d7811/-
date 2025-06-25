import random
from typing import List, Dict

QUESTIONS: List[Dict] = [
    {
        "text": "من هو اللاعب الذي سجل أكبر عدد من الأهداف في تاريخ كأس العالم؟",
        "options": ["بيليه", "ميروسلاف كلوزه", "رونالدو", "ميسي"],
        "correct": 1,
        "difficulty": "medium"
    },
    {
        "text": "أي منتخب فاز بكأس العالم 2018؟",
        "options": ["ألمانيا", "البرازيل", "فرنسا", "إسبانيا"],
        "correct": 2,
        "difficulty": "medium"
    },
    {
        "text": "من هو هداف الدوري الإنجليزي الممتاز موسم 2022/2023؟",
        "options": ["محمد صلاح", "هالاند", "كاين", "سون"],
        "correct": 1,
        "difficulty": "easy"
    },
    # يمكنك إضافة المزيد من الأسئلة هنا
]

def get_random_questions(num: int = 5, difficulty: str = None) -> List[Dict]:
    """إرجاع قائمة عشوائية من الأسئلة"""
    if difficulty:
        filtered = [q for q in QUESTIONS if q["difficulty"] == difficulty]
        return random.sample(filtered, min(num, len(filtered)))
    return random.sample(QUESTIONS, min(num, len(QUESTIONS)))