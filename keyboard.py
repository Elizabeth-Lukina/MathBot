"""
Модуль для создания клавиатур и интерфейса Telegram бота
Содержит все кнопки, меню и элементы пользовательского интерфейса
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from typing import List, Optional, Dict, Any
from config import SUBSCRIPTION_PLANS, SOLUTION_PACKAGES, EXAMPLE_PROBLEMS

class BotKeyboard:
    """Класс для создания клавиатур бота"""
    
    @staticmethod
    def get_main_menu() -> ReplyKeyboardMarkup:
        """Основное меню бота"""
        keyboard = [
            ["🎯 Решить задачу", "💰 Баланс"],
            ["📊 История", "🎓 Примеры"],
            ["💎 Тарифы", "🆘 Помощь"]
        ]
        
        return ReplyKeyboardMarkup(
            keyboard, 
            resize_keyboard=True,
            one_time_keyboard=False
        )
    
    @staticmethod
    def get_input_type_keyboard() -> InlineKeyboardMarkup:
        """Клавиатура выбора типа ввода задачи"""
        keyboard = [
            [InlineKeyboardButton("📸 Отправить фото", callback_data="input_photo")],
            [InlineKeyboardButton("📝 Написать текстом", callback_data="input_text")],
            [InlineKeyboardButton("◀️ Назад", callback_data="back_main")]
        ]
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_balance_keyboard(user_balance: Dict[str, Any]) -> InlineKeyboardMarkup:
        """Клавиатура для раздела баланса"""
        keyboard = []
        
        # Показываем кнопки покупки если баланс низкий
        total_solutions = user_balance['free_solutions'] + user_balance['paid_solutions']
        subscription_active = user_balance['subscription']['active']
        
        if not subscription_active and total_solutions < 5:
            keyboard.append([InlineKeyboardButton("💳 Купить решения", callback_data="buy_solutions")])
            keyboard.append([InlineKeyboardButton("📋 Оформить подписку", callback_data="buy_subscription")])
        
        keyboard.extend([
            [InlineKeyboardButton("📊 История решений", callback_data="show_history")],
            [InlineKeyboardButton("◀️ Главное меню", callback_data="back_main")]
        ])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_subscription_plans_keyboard() -> InlineKeyboardMarkup:
        """Клавиатура с тарифными планами"""
        keyboard = []
        
        for plan_id, plan_info in SUBSCRIPTION_PLANS.items():
            text = f"{plan_info['name']} - {plan_info['price']}{plan_info['currency']}/мес"
            keyboard.append([InlineKeyboardButton(text, callback_data=f"sub_{plan_id}")])
        
        keyboard.append([InlineKeyboardButton("◀️ Назад", callback_data="back_balance")])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_solution_packages_keyboard() -> InlineKeyboardMarkup:
        """Клавиатура с пакетами решений"""
        keyboard = []
        
        for pack_id, pack_info in SOLUTION_PACKAGES.items():
            text = f"{pack_info['name']} - {pack_info['price']}{pack_info['currency']}"
            if pack_info.get('discount'):
                text += " 🔥"
            keyboard.append([InlineKeyboardButton(text, callback_data=f"pack_{pack_id}")])
        
        keyboard.append([InlineKeyboardButton("◀️ Назад", callback_data="back_balance")])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_examples_keyboard() -> InlineKeyboardMarkup:
        """Клавиатура с примерами задач"""
        keyboard = []
        
        for i, example in enumerate(EXAMPLE_PROBLEMS[:5]):  # Показываем первые 5 примеров
            short_example = example[:30] + "..." if len(example) > 30 else example
            keyboard.append([InlineKeyboardButton(short_example, callback_data=f"example_{i}")])
        
        keyboard.append([InlineKeyboardButton("◀️ Главное меню", callback_data="back_main")])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_history_keyboard(page: int = 0) -> InlineKeyboardMarkup:
        """Клавиатура для навигации по истории"""
        keyboard = []
        
        # Кнопки навигации по страницам
        nav_buttons = []
        if page > 0:
            nav_buttons.append(InlineKeyboardButton("◀️ Пред.", callback_data=f"history_page_{page-1}"))
        
        nav_buttons.append(InlineKeyboardButton("▶️ След.", callback_data=f"history_page_{page+1}"))
        
        if nav_buttons:
            keyboard.append(nav_buttons)
        
        keyboard.extend([
            [InlineKeyboardButton("🗑 Очистить историю", callback_data="clear_history")],
            [InlineKeyboardButton("◀️ Назад", callback_data="back_balance")]
        ])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_solution_result_keyboard(solution_id: Optional[str] = None) -> InlineKeyboardMarkup:
        """Клавиатура после получения решения"""
        keyboard = [
            [InlineKeyboardButton("🔄 Решить еще", callback_data="solve_another")],
            [InlineKeyboardButton("📊 Моя история", callback_data="show_history")]
        ]
        
        if solution_id:
            keyboard.insert(0, [InlineKeyboardButton("📤 Поделиться", callback_data=f"share_{solution_id}")])
        
        keyboard.append([InlineKeyboardButton("◀️ Главное меню", callback_data="back_main")])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_payment_keyboard(item_type: str, item_id: str) -> InlineKeyboardMarkup:
        """Клавиатура для оплаты"""
        keyboard = [
            [InlineKeyboardButton("💳 Оплатить картой", callback_data=f"pay_card_{item_type}_{item_id}")],
            [InlineKeyboardButton("📱 Оплата по QR", callback_data=f"pay_qr_{item_type}_{item_id}")],
            [InlineKeyboardButton("◀️ Отмена", callback_data="back_balance")]
        ]
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_admin_keyboard() -> InlineKeyboardMarkup:
        """Клавиатура для администратора (только для разработчиков)"""
        keyboard = [
            [InlineKeyboardButton("📈 Статистика", callback_data="admin_stats")],
            [InlineKeyboardButton("💰 Расходы OpenAI", callback_data="admin_openai_costs")],
            [InlineKeyboardButton("👥 Активные пользователи", callback_data="admin_users")],
            [InlineKeyboardButton("💾 Резервная копия БД", callback_data="admin_backup")],
            [InlineKeyboardButton("◀️ Главное меню", callback_data="back_main")]
        ]
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_confirmation_keyboard(action: str, item_id: str = "") -> InlineKeyboardMarkup:
        """Клавиатура подтверждения действия"""
        keyboard = [
            [InlineKeyboardButton("✅ Да", callback_data=f"confirm_{action}_{item_id}")],
            [InlineKeyboardButton("❌ Нет", callback_data=f"cancel_{action}")]
        ]
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_help_keyboard() -> InlineKeyboardMarkup:
        """Клавиатура для раздела помощи"""
        keyboard = [
            [InlineKeyboardButton("📝 Как решать задачи", callback_data="help_howto")],
            [InlineKeyboardButton("💰 О тарифах", callback_data="help_pricing")],
            [InlineKeyboardButton("🤖 О боте", callback_data="help_about")],
            [InlineKeyboardButton("📞 Связь с поддержкой", url="https://t.me/support_mathbot")],
            [InlineKeyboardButton("◀️ Главное меню", callback_data="back_main")]
        ]
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def get_problem_type_keyboard() -> InlineKeyboardMarkup:
        """Клавиатура выбора типа задачи (для продвинутых пользователей)"""
        keyboard = [
            [InlineKeyboardButton("📐 Уравнения", callback_data="type_equations")],
            [InlineKeyboardButton("∫ Интегралы", callback_data="type_integrals")],
            [InlineKeyboardButton("d/dx Производные", callback_data="type_derivatives")],
            [InlineKeyboardButton("📊 Статистика", callback_data="type_statistics")],
            [InlineKeyboardButton("🔢 Арифметика", callback_data="type_arithmetic")],
            [InlineKeyboardButton("◀️ Назад", callback_data="back_main")]
        ]
        
        return InlineKeyboardMarkup(keyboard)

    # В keyboard.py добавляем:

    @staticmethod
    def get_solution_mode_keyboard() -> InlineKeyboardMarkup:
        """Клавиатура выбора режима решения"""
        keyboard = [
            [InlineKeyboardButton("🚀 Быстрый ответ", callback_data="mode_quick")],
            [InlineKeyboardButton("📚 Экзамен", callback_data="mode_exam")],
            [InlineKeyboardButton("👨‍🏫 Репетитор", callback_data="mode_tutor")],
            [InlineKeyboardButton("◀️ Назад", callback_data="back_main")]
        ]

        return InlineKeyboardMarkup(keyboard)

    @staticmethod
    def get_confirm_mode_keyboard(selected_mode: str) -> InlineKeyboardMarkup:
        """Клавиатура подтверждения выбора режима"""
        keyboard = [
            [InlineKeyboardButton("✅ Да, решить в этом режиме", callback_data=f"confirm_mode_{selected_mode}")],
            [InlineKeyboardButton("🔄 Выбрать другой режим", callback_data="change_mode")],
            [InlineKeyboardButton("◀️ Отмена", callback_data="back_main")]
        ]

        return InlineKeyboardMarkup(keyboard)

# Создаем глобальный экземпляр клавиатуры
bot_keyboard = BotKeyboard()