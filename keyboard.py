from telebot import types


class BotKeyboard:
    def main_menu(self):
        """Главное меню"""
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.row("🎯 Решить задачу", "💰 Мой баланс")
        markup.row("💳 Купить решения", "📊 История")
        markup.row("🆘 Помощь")
        return markup

    def buy_menu(self):
        """Меню покупок"""
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔔 Подписки", callback_data="buy_subscription"))
        markup.add(types.InlineKeyboardButton("📦 Пакеты решений", callback_data="buy_package"))
        return markup

    def after_solution_menu(self):
        """Меню после решения"""
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🎯 Решить еще", callback_data="solve_another"))
        markup.add(types.InlineKeyboardButton("💳 Купить еще", callback_data="buy_more"))
        return markup

    def solve_options(self):
        """Опции решения"""
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📝 Текст", callback_data="input_text"))
        markup.add(types.InlineKeyboardButton("📸 Фото", callback_data="input_photo"))
        return markup


# Глобальный экземпляр
bot_keyboard = BotKeyboard()