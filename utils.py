"""
Вспомогательные утилиты для Telegram бота
Содержит функции форматирования, валидации и общие утилиты
"""

import re
import html
import logging
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from telegram import Update, User as TelegramUser
from telegram.constants import ParseMode

logger = logging.getLogger(__name__)

class MessageFormatter:
    """Класс для форматирования сообщений"""
    
    @staticmethod
    def format_welcome_message(user_name: str, free_solutions: int) -> str:
        """Форматирование приветственного сообщения"""
        return f"""
🎓 *Добро пожаловать в МатБот, {html.escape(user_name)}!*

Я помогу решить любую математическую задачу:
• Отправьте фото задачи 📸
• Напишите задачу текстом 📝  
• Получите подробное решение с объяснениями 💡

🎁 *У вас есть {free_solutions} бесплатных решений!*

Используйте кнопки ниже для навигации или команды:
/help - справка по использованию
/examples - примеры задач
        """
    
    @staticmethod
    def format_balance_message(balance_data: Dict[str, Any], username: str) -> str:
        """Форматирование сообщения о балансе"""
        free_solutions = balance_data['free_solutions']
        paid_solutions = balance_data['paid_solutions']
        subscription = balance_data['subscription']
        
        message = f"💰 *Ваш баланс, {html.escape(username)}*\n\n"
        
        # Информация о решениях
        if subscription['active']:
            subscription_type = subscription['type']
            end_date = subscription['end_date']
            message += f"✅ *Активная подписка:* {subscription_type}\n"
            message += f"📅 *Действует до:* {end_date}\n"
            message += f"🎯 *Решений:* Неограниченно\n\n"
        else:
            total_solutions = free_solutions + paid_solutions
            message += f"🎯 *Доступно решений:* {total_solutions}\n"
            message += f"   • Бесплатных: {free_solutions}\n"
            message += f"   • Оплаченных: {paid_solutions}\n\n"
            
            if total_solutions < 3:
                message += "⚠️ *У вас заканчиваются решения!*\n"
                message += "Рассмотрите покупку пакета или подписку.\n\n"
        
        return message
    
    @staticmethod
    def format_solution_message(solution_data: Dict[str, Any]) -> str:
        """Форматирование сообщения с решением"""
        problem_text = solution_data.get('problem_text', '')
        solution = solution_data.get('solution', '')
        explanation = solution_data.get('explanation', '')
        problem_type = solution_data.get('problem_type', 'неизвестный')
        method = solution_data.get('method', 'sympy')
        latex_formatted = solution_data.get('latex_formatted', '')
        
        message = f"📝 *Задача:*\n{html.escape(problem_text)}\n\n"
        message += f"🧮 *Тип задачи:* {problem_type}\n"
        message += f"⚙️ *Метод решения:* {'SymPy' if method == 'sympy' else 'AI'}\n\n"
        
        # Форматируем ответ с LaTeX (если есть) в виде code block
        if latex_formatted:
            message += f"✅ *Ответ (LaTeX):*\n```\n{latex_formatted}\n```\n\n"
        
        message += f"✅ *Ответ:*\n`{html.escape(str(solution))}`\n\n"
        
        if explanation:
            message += f"💡 *Объяснение:*\n{html.escape(explanation)}\n\n"
        
        # Добавляем шаги решения если есть
        steps = solution_data.get('steps', [])
        if steps:
            message += "📋 *Шаги решения:*\n"
            for i, step in enumerate(steps[:5], 1):  # Ограничиваем до 5 шагов
                message += f"{i}. {html.escape(step)}\n"
            
            if len(steps) > 5:
                message += f"... и еще {len(steps) - 5} шагов\n"
            message += "\n"
        
        return message
    
    @staticmethod
    def format_history_message(history_data: List[Dict[str, Any]], page: int = 0) -> str:
        """Форматирование сообщения с историей решений"""
        if not history_data:
            return "📊 *История решений пуста*\n\nВы еще не решали задач с помощью бота."
        
        message = f"📊 *История решений* (страница {page + 1})\n\n"
        
        for i, record in enumerate(history_data):
            problem_text = record['problem_text']
            created_at = record['created_at']
            problem_type = record.get('problem_type', 'неизвестный')
            
            # Обрезаем текст задачи для краткости
            short_problem = (problem_text[:50] + "...") if len(problem_text) > 50 else problem_text
            
            # Форматируем дату
            try:
                date_obj = datetime.fromisoformat(created_at)
                date_str = date_obj.strftime("%d.%m.%Y %H:%M")
            except:
                date_str = created_at
            
            message += f"{i + 1}. *{problem_type}*\n"
            message += f"   📝 {html.escape(short_problem)}\n"
            message += f"   📅 {date_str}\n\n"
        
        return message
    
    @staticmethod
    def format_subscription_info(plan_id: str) -> str:
        """Форматирование информации о подписке"""
        from config import SUBSCRIPTION_PLANS
        
        if plan_id not in SUBSCRIPTION_PLANS:
            return "❌ План подписки не найден"
        
        plan = SUBSCRIPTION_PLANS[plan_id]
        
        message = f"💎 *{plan['name']}*\n\n"
        message += f"💰 *Цена:* {plan['price']} {plan['currency']}/месяц\n"
        message += f"📅 *Период:* {plan['duration_days']} дней\n"
        
        if plan['solutions_limit'] == -1:
            message += f"🎯 *Решений:* Неограниченно\n"
        else:
            message += f"🎯 *Решений:* до {plan['solutions_limit']} в месяц\n"
        
        message += f"📋 *Описание:* {plan['description']}\n\n"
        
        # Дополнительные функции
        if 'features' in plan:
            message += "*Дополнительные возможности:*\n"
            for feature in plan['features']:
                if feature == 'latex_export':
                    message += "• 📄 Экспорт решений в LaTeX\n"
        
        return message
    
    @staticmethod
    def format_error_message(error_type: str, details: str = "") -> str:
        """Форматирование сообщений об ошибках"""
        error_messages = {
            'no_solutions': "😔 *У вас закончились решения!*\n\nВыберите один из вариантов:\n• Купить пакет решений 💰\n• Оформить подписку 📋\n• Обратиться в поддержку 🆘",
            'ocr_failed': "❌ *Не удалось распознать текст с фотографии*\n\nПопробуйте:\n• Сделать более четкое фото\n• Лучше осветить текст\n• Написать задачу текстом",
            'no_math_found': "❌ *Не найдена математическая задача*\n\nУбедитесь, что текст содержит:\n• Математические символы\n• Уравнения или выражения\n• Четко сформулированную задачу",
            'solving_failed': "❌ *Не удалось решить задачу*\n\nВозможные причины:\n• Некорректное условие\n• Слишком сложная задача\n• Неподдерживаемый тип задачи",
            'general_error': f"❌ *Произошла ошибка*\n\n{details}\n\nПопробуйте еще раз или обратитесь в поддержку."
        }
        
        return error_messages.get(error_type, error_messages['general_error'])

class UserDataExtractor:
    """Класс для извлечения данных пользователя"""
    
    @staticmethod
    def extract_user_data(update: Update) -> Dict[str, Any]:
        """Извлечение данных пользователя из обновления"""
        user = update.effective_user
        if not user:
            return {}
        
        return {
            'user_id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'language_code': user.language_code or 'ru'
        }
    
    @staticmethod
    def get_display_name(user_data: Dict[str, Any]) -> str:
        """Получение имени для отображения"""
        first_name = user_data.get('first_name', '')
        last_name = user_data.get('last_name', '')
        username = user_data.get('username', '')
        
        if first_name:
            return first_name + (f" {last_name}" if last_name else "")
        elif username:
            return f"@{username}"
        else:
            return "Пользователь"

class ValidationUtils:
    """Утилиты для валидации данных"""
    
    @staticmethod
    def is_valid_mathematical_text(text: str) -> bool:
        """Проверка, является ли текст математической задачей"""
        if not text or len(text.strip()) < 2:
            return False
        
        # Математические индикаторы
        math_patterns = [
            r'\d+',  # Цифры
            r'[+\-*/=<>]',  # Математические операторы
            r'\b(sin|cos|tan|log|ln|sqrt|integral|производная|уравнение)\b',  # Функции
            r'[xyz]',  # Переменные
            r'[∫∑∞π]'  # Специальные символы
        ]
        
        score = 0
        text_lower = text.lower()
        
        for pattern in math_patterns:
            if re.search(pattern, text_lower):
                score += 1
        
        return score >= 2
    
    @staticmethod
    def clean_mathematical_input(text: str) -> str:
        """Очистка математического ввода"""
        # Удаляем лишние пробелы
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Заменяем некоторые Unicode символы
        replacements = {
            '—': '-',
            '–': '-',
            '×': '*',
            '÷': '/',
            '²': '**2',
            '³': '**3'
        }
        
        for old, new in replacements.items():
            text = text.replace(old, new)
        
        return text
    
    @staticmethod
    def validate_image_size(file_size: int, max_size: int = 10 * 1024 * 1024) -> bool:
        """Проверка размера изображения"""
        return file_size <= max_size

class SecurityUtils:
    """Утилиты безопасности"""
    
    @staticmethod
    def hash_user_id(user_id: int) -> str:
        """Хеширование ID пользователя для логов"""
        return hashlib.sha256(str(user_id).encode()).hexdigest()
    
    @staticmethod
    def is_admin_user(user_id: int) -> bool:
        """Проверка, является ли пользователь администратором"""
        from config import DEVELOPER_IDS
        return user_id in DEVELOPER_IDS
    
    @staticmethod
    def sanitize_text_for_log(text: str, max_length: int = 100) -> str:
        """Очистка текста для логов"""
        if len(text) > max_length:
            text = text[:max_length] + "..."
        
        # Удаляем потенциально опасные символы
        text = re.sub(r'[^\w\s\-+*/=().,;:]', '', text)
        
        return text

class TimeUtils:
    """Утилиты для работы со временем"""
    
    @staticmethod
    def format_datetime(dt: datetime) -> str:
        """Форматирование даты и времени"""
        return dt.strftime("%d.%m.%Y %H:%M")
    
    @staticmethod
    def get_subscription_end_date(duration_days: int) -> datetime:
        """Вычисление даты окончания подписки"""
        return datetime.now() + timedelta(days=duration_days)
    
    @staticmethod
    def is_subscription_active(end_date: str) -> bool:
        """Проверка активности подписки"""
        try:
            end_dt = datetime.fromisoformat(end_date)
            return end_dt > datetime.now()
        except:
            return False

# Создаем глобальные экземпляры утилит
message_formatter = MessageFormatter()
user_data_extractor = UserDataExtractor()
validation_utils = ValidationUtils()
security_utils = SecurityUtils()
time_utils = TimeUtils()