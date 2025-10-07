import os
import logging
from datetime import datetime

# Токен бота
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', '8145161819:AAHSeyx_VYThcTEClypiZmRrOAMViCK3ZX4')

# Создаем папку для логов если ее нет
os.makedirs('debug_logs', exist_ok=True)
# Настройка логирования
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'debug_logs/bot_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# Настройки монетизации
SUBSCRIPTION_PRICES = {
    'premium': 299,    # Премиум подписка
    'basic': 149       # Базовая подписка
}

SOLUTION_PACKAGES = {
    '10': 99,    # 10 решений
    '25': 199,   # 25 решений
    '50': 299    # 50 решений
}

# Бесплатные решения
FREE_SOLUTIONS = 3

# Настройки OCR
OCR_LANGUAGES = ['ru', 'en']
# Поддерживаемые типы математических задач
SUPPORTED_MATH_TYPES = [
    'equations',      # Уравнения
    'integrals',      # Интегралы
    'derivatives',    # Производные
    'arithmetic',     # Арифметика
    'trigonometry',   # Тригонометрия
    'differential',   # Дифференциальные уравнения
    'statistics',     # Статистика
    'algebra',        # Алгебра
    'vectors'         # Векторная алгебра
]
