"""
Конфигурация Telegram бота для решения математических задач
Содержит настройки подписок, цены, лимиты и системные параметры
"""

import os
from dotenv import load_dotenv

load_dotenv()
# Токен Telegram бота
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

# OpenAI API ключ
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Переключается на True если Tesseract не работает
USE_OPENAI_VISION = False
USE_OPENAI_VISION_FALLBACK = True  # Разрешить fallback на OpenAI Vision
OPENAI_VISION_MAX_COST = 0.10  # Максимальная стоимость за распознавание в USD

# Путь к базе данных SQLite
DATABASE_PATH = 'math_bot.db'

# Настройки OCR
OCR_LANGUAGE = 'rus+eng'
OCR_CONFIG = '--psm 6'

# Режимы решения задач
SOLUTION_MODES = {
    'quick': {
        'name': '🚀 Быстрый ответ',
        'description': 'Только ответ для списывания',
        'use_sympy': True,
        'use_ai_explanation': False,
        'cost_multiplier': 1.0,
        'emoji': '🚀'
    },
    'exam': {
        'name': '📚 Экзамен',
        'description': 'Пошаговое решение с объяснениями',
        'use_sympy': True,
        'use_ai_explanation': True,
        'cost_multiplier': 1.5,
        'emoji': '📚'
    },
    'tutor': {
        'name': '👨‍🏫 Репетитор',
        'description': 'Интерактивное обучение с подсказками',
        'use_sympy': True,
        'use_ai_explanation': True,
        'cost_multiplier': 2.0,
        'emoji': '👨‍🏫'
    }
}

BOT_MESSAGES = {
    'welcome': """
🎓 Добро пожаловать в МатБот!
Я помогу решить любую математическую задачу:
• Отправьте фото задачи 📸
• Напишите задачу текстом 📝  
• Получите подробное решение с объяснениями 💡

У вас есть {free_solutions} бесплатных решений! 🎁

Используйте кнопки ниже для навигации:
    """,

    'mode_selection': """
🎯 *Выберите режим решения:*

🚀 *Быстрый ответ* - только ответ для списывания
📚 *Экзамен* - пошаговое решение с объяснениями  
👨‍🏫 *Репетитор* - интерактивное обучение с подсказками
    """,

    'quick_mode_selected': "🚀 Выбран режим *Быстрый ответ* - получайте только ответы",
    'exam_mode_selected': "📚 Выбран режим *Экзамен* - получайте подробные решения",
    'tutor_mode_selected': "👨‍🏫 Выбран режим *Репетитор* - обучайтесь с подсказками",

    'help': """
🆘 Справка по использованию МатБота

📸 *Фото задач*: Сделайте четкое фото математической задачи
📝 *Текстовые задачи*: Напишите задачу обычным текстом

🎯 *Режимы решения:*
• Быстрый ответ - только ответ для списывания
• Экзамен - подробное решение с объяснениями  
• Репетитор - обучение с подсказками

💰 *Система оплаты:*
• 3 бесплатных решения для новых пользователей
• Подписки и пакеты решений

Нужна помощь? Обратитесь в поддержку
""",

    'no_solutions': """
😔 У вас закончились решения!

Выберите один из вариантов:
• Купить пакет решений 💰
• Оформить подписку 📋
• Обратиться в поддержку 🆘
    """,

    'processing': "🔄 Обрабатываю задачу... Пожалуйста, подождите.",
    'ocr_processing': "👀 Распознаю текст с фотографии...",
    'solving': "🧮 Решаю задачу...",
    'generating_explanation': "💡 Генерирую подробное объяснение...",

    'error_general': "❌ Произошла ошибка. Попробуйте еще раз или обратитесь в поддержку.",
    'error_ocr': "❌ Не удалось распознать текст с фотографии. Убедитесь, что изображение четкое.",
    'error_no_math': "❌ Не удалось найти математическую задачу в тексте.",
    'error_solving': "❌ Не удалось решить задачу. Проверьте корректность условия.",
    'error_openai': "❌ Ошибка при генерации объяснения. Попробуйте позже."
}

SUBSCRIPTION_PLANS = {
    'school': {
        'name': 'Школьник',
        'price': 299,
        'currency': '₽',
        'duration_days': 30,
        'solutions_limit': 50,
        'description': 'Идеально для школьников - до 50 задач в месяц',
        'allowed_modes': ['quick', 'exam']
    },
    'student': {
        'name': 'Студент',
        'price': 599,
        'currency': '₽',
        'duration_days': 30,
        'solutions_limit': -1,
        'description': 'Для студентов - неограниченное количество задач',
        'allowed_modes': ['quick', 'exam', 'tutor']
    }
}

SOLUTION_PACKAGES = {
    'pack_1': {
        'solutions': 1,
        'price': 49,
        'currency': '₽',
        'name': '1 решение'
    },
    'pack_10': {
        'solutions': 10,
        'price': 149,
        'currency': '₽',
        'name': '10 решений',
        'discount': True
    }
}

FREE_SOLUTIONS_FOR_NEW_USERS = 10000
OPENAI_MODEL = "gpt-4o"
OPENAI_MAX_TOKENS = 2000
OPENAI_TEMPERATURE = 0.3

SUPPORTED_MATH_TYPES = [
    'equations', 'integrals', 'derivatives', 'arithmetic',
    'trigonometry', 'algebra'
]

EXAMPLE_PROBLEMS = [
    "Найти производную: f(x) = x² + 3x - 5",
    "Решить уравнение: 2x + 5 = 13",
    "Вычислить интеграл: ∫(x² + 1)dx",
    "Найти cos(π/4)",
    "Решить систему: x + y = 5, 2x - y = 1"
]


MAX_IMAGE_SIZE = 10 * 1024 * 1024
MAX_TEXT_LENGTH = 2000
MAX_SOLUTIONS_PER_DAY = 200
DEVELOPER_IDS = []
