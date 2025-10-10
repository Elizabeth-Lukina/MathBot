import logging
import os
import asyncio
from typing import Dict, Any, Optional

from telegram import Update
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ContextTypes, filters
)
from telegram.constants import ParseMode

# Импортируем модули бота
from config import (
    TELEGRAM_TOKEN, BOT_MESSAGES, EXAMPLE_PROBLEMS,
    SUBSCRIPTION_PLANS, SOLUTION_MODES)
from database import db
from image_processor import image_processor
from hybrid_solver import hybrid_solver
from keyboard import bot_keyboard
from utils import (
    message_formatter, user_data_extractor,
    validation_utils, security_utils
)

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)
logging.getLogger("httpx").setLevel(logging.WARNING)


class MathBot:
    """Основной класс Telegram бота с логичной архитектурой"""

    def __init__(self, token: str):
        if not token or token == 'YOUR_TELEGRAM_BOT_TOKEN_HERE':
            raise ValueError("Токен бота не установлен! Укажите TELEGRAM_TOKEN в config.py")

        self.token = token
        self.application = None

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик команды /start"""
        try:
            user_data = user_data_extractor.extract_user_data(update)
            user_id = user_data['user_id']

            # Создаем или обновляем пользователя в базе
            db.create_or_update_user(user_data)

            # Получаем информацию о пользователе
            user_info = db.get_user(user_id)
            display_name = user_data_extractor.get_display_name(user_data)
            free_solutions = user_info['free_solutions'] if user_info else 3

            # Отправляем приветственное сообщение
            welcome_message = message_formatter.format_welcome_message(display_name, free_solutions)
            keyboard = bot_keyboard.get_main_menu()

            await update.message.reply_text(
                welcome_message,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboard
            )

            logger.info(f"Пользователь {security_utils.hash_user_id(user_id)} запустил бота")

        except Exception as e:
            logger.error(f"Ошибка в start_command: {e}")
            await update.message.reply_text(
                "❌ Произошла ошибка при запуске. Попробуйте еще раз.",
                parse_mode=ParseMode.MARKDOWN
            )

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик команды /help"""
        try:
            help_message = BOT_MESSAGES['help']
            keyboard = bot_keyboard.get_help_keyboard()

            await update.message.reply_text(
                help_message,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboard
            )

        except Exception as e:
            logger.error(f"Ошибка в help_command: {e}")
            await update.message.reply_text(
                "❌ Ошибка при показе справки.",
                parse_mode=ParseMode.MARKDOWN
            )

    async def handle_main_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик кнопок главного меню"""
        try:
            message_text = update.message.text

            if message_text == "🎯 Решить задачу":
                await self.handle_solution_mode_selection(update, context)
            elif message_text == "💰 Баланс":
                await self.show_balance(update, context)
            elif message_text == "📊 История":
                await self.show_history(update, context)
            elif message_text == "🎓 Примеры":
                await self.show_examples(update, context)
            elif message_text == "💎 Тарифы":
                await self.show_subscriptions(update, context)
            elif message_text == "🆘 Помощь":
                await self.help_command(update, context)
            else:
                await update.message.reply_text(
                    "🤔 Не понимаю команду. Используйте кнопки меню или /help",
                    reply_markup=bot_keyboard.get_main_menu()
                )

        except Exception as e:
            logger.error(f"Ошибка обработки меню: {e}")
            await update.message.reply_text(
                "❌ Ошибка обработки команды.",
                parse_mode=ParseMode.MARKDOWN
            )

    async def handle_solution_mode_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Показать выбор режима решения"""
        try:
            keyboard = bot_keyboard.get_solution_mode_keyboard()  # Правильное название метода

            await update.message.reply_text(
                BOT_MESSAGES['mode_selection'],
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboard
            )

        except Exception as e:
            logger.error(f"Ошибка выбора режима: {e}")

    async def handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик inline кнопок"""
        try:
            query = update.callback_query
            await query.answer()

            data = query.data

            # Обработка выбора режима
            if data.startswith('mode_'):
                await self.handle_mode_selection(query, context, data)
            elif data.startswith('confirm_mode_'):
                await self.handle_mode_confirmation(query, context, data)
            elif data == "change_mode":
                await self.handle_solution_mode_callback(query, context)

            # Обработка ввода задачи
            elif data == "input_photo":
                await query.edit_message_text("📸 Отправьте фото задачи...")
            elif data == "input_text":
                await query.edit_message_text("📝 Введите текст задачи...")

            # Навигация
            elif data == "back_main":
                await self.show_main_menu_callback(query, context)
            elif data == "back_balance":
                await self.show_balance_callback(query, context)

            # Примеры задач
            elif data.startswith("example_"):
                await self.solve_example_problem(query, context, data)

        except Exception as e:
            logger.error(f"Ошибка обработки callback: {e}")
            await query.edit_message_text("❌ Ошибка обработки запроса")

    async def handle_mode_selection(self, query, context: ContextTypes.DEFAULT_TYPE, callback_data: str) -> None:
        """Обработка выбора режима"""
        try:
            mode = callback_data.replace('mode_', '')
            context.user_data['selected_mode'] = mode

            mode_info = SOLUTION_MODES.get(mode, {})
            confirm_text = f"""
        {mode_info.get('emoji', '🎯')} *{mode_info.get('name', 'Режим')}*

        {mode_info.get('description', '')}

        ✅ *Подтвердите выбор режима*
                """

            keyboard = bot_keyboard.get_confirm_mode_keyboard(mode)  # Правильное название метода
            if not keyboard:
                raise ValueError("Клавиатура не создана")

            await query.edit_message_text(
                confirm_text,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboard
            )
        except Exception as e:
            logger.error(f"Ошибка в handle_mode_selection: {e}")
            await query.edit_message_text("❌ Ошибка выбора режима")

    async def handle_mode_confirmation(self, query, context: ContextTypes.DEFAULT_TYPE, callback_data: str) -> None:
        """Обработка подтверждения режима"""
        try:
            mode = callback_data.replace('confirm_mode_', '')
            context.user_data['solution_mode'] = mode

            # Сообщения подтверждения
            mode_messages = {
                'quick': BOT_MESSAGES['quick_mode_selected'],
                'exam': BOT_MESSAGES['exam_mode_selected'],
                'tutor': BOT_MESSAGES['tutor_mode_selected']
            }

            await query.edit_message_text(
                mode_messages.get(mode, "✅ Режим выбран"),
                parse_mode=ParseMode.MARKDOWN
            )

            # Предлагаем ввести задачу
            keyboard = bot_keyboard.get_input_type_keyboard()  # Правильное название метода
            if not keyboard:
                raise ValueError("Клавиатура ввода не создана")

            await query.message.reply_text(
                "📝 Выберите способ ввода задачи:",
                reply_markup=keyboard
            )
        except Exception as e:
            logger.error(f"Ошибка в handle_mode_confirmation: {e}")
            await query.edit_message_text("❌ Ошибка подтверждения режима")

    async def handle_text_problem(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработка текстовой математической задачи"""
        try:
            print(f"Получена задача: {update.message.text}")

            user_data = user_data_extractor.extract_user_data(update)
            user_id = user_data['user_id']
            problem_text = update.message.text

            # Проверяем баланс
            if not db.use_solution(user_id):
                await update.message.reply_text(
                    BOT_MESSAGES['no_solutions'],
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=bot_keyboard.get_balance_keyboard(db.get_user_balance(user_id))
                )
                return

            # Получаем выбранный режим (по умолчанию - exam)
            solution_mode = context.user_data.get('solution_mode', 'exam')

            # Отправляем сообщение о обработке
            processing_message = await update.message.reply_text(
                BOT_MESSAGES['solving'],
                parse_mode=ParseMode.MARKDOWN
            )

            # Решаем задачу с выбранным режимом
            solution_result = hybrid_solver.solve_with_mode(problem_text, solution_mode)

            if solution_result['success']:
                # Сохраняем решение
                solution_data = {
                    'user_id': user_id,
                    'problem_text': problem_text,
                    'problem_type': solution_result.get('problem_type', 'неизвестный'),
                    'solution_method': 'hybrid',
                    'solution_result': solution_result['solution'],
                    'explanation': solution_result.get('explanation', ''),
                    'processing_time': solution_result.get('processing_time', 0),
                    'success': True
                }
                db.save_solution(solution_data)

                # Получаем клавиатуру для результата
                keyboard = bot_keyboard.get_solution_result_keyboard()  # Без параметра, так как solution_id не передается

                await processing_message.edit_text(
                    solution_result['explanation'],
                    reply_markup=keyboard
                )
            else:
                await processing_message.edit_text(
                    "❌ Не удалось решить задачу. Попробуйте другой режим или проверьте условие.",
                    parse_mode=ParseMode.MARKDOWN
                )

        except Exception as e:
            logger.error(f"Ошибка решения текстовой задачи: {e}")
            await update.message.reply_text(
                "❌ Ошибка при решении задачи.",
                parse_mode=ParseMode.MARKDOWN
            )

    async def handle_photo_problem(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработка задачи с фото"""
        try:
            user_data = user_data_extractor.extract_user_data(update)
            user_id = user_data['user_id']

            # Проверяем баланс
            if not db.use_solution(user_id):
                await update.message.reply_text(
                    BOT_MESSAGES['no_solutions'],
                    parse_mode=ParseMode.MARKDOWN
                )
                return

            processing_message = await update.message.reply_text(
                BOT_MESSAGES['ocr_processing'],
                parse_mode=ParseMode.MARKDOWN
            )

            # Обрабатываем фото
            photo = update.message.photo[-1]
            photo_file = await photo.get_file()
            photo_data = await photo_file.download_as_bytearray()

            extracted_text = image_processor.process_image(bytes(photo_data))

            if not extracted_text:
                await processing_message.edit_text(BOT_MESSAGES['error_ocr'])
                return

            if not image_processor.validate_mathematical_content(extracted_text):
                await processing_message.edit_text(BOT_MESSAGES['error_no_math'])
                return

            # Решаем задачу
            solution_mode = context.user_data.get('solution_mode', 'exam')
            await processing_message.edit_text(BOT_MESSAGES['solving'])

            solution_result = hybrid_solver.solve_with_mode(extracted_text, solution_mode)

            if solution_result['success']:
                solution_data = {
                    'user_id': user_id,
                    'problem_text': extracted_text,
                    'problem_type': solution_result.get('problem_type', 'неизвестный'),
                    'solution_method': 'hybrid',
                    'solution_result': solution_result['solution'],
                    'explanation': solution_result.get('explanation', ''),
                    'processing_time': solution_result.get('processing_time', 0),
                    'success': True
                }
                db.save_solution(solution_data)

                solution_message = message_formatter.format_solution_message(solution_data)
                keyboard = bot_keyboard.get_solution_result_keyboard()

                await processing_message.edit_text(
                    solution_message,
                    parse_mode=ParseMode.MARKDOWN,
                    reply_markup=keyboard
                )
            else:
                await processing_message.edit_text(BOT_MESSAGES['error_solving'])

        except Exception as e:
            logger.error(f"Ошибка обработки фото: {e}")
            await update.message.reply_text(BOT_MESSAGES['error_general'])

    # Дополнительные методы (упрощенные)
    async def show_balance(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Показать баланс"""
        user_data = user_data_extractor.extract_user_data(update)
        balance_data = db.get_user_balance(user_data['user_id'])
        username = user_data_extractor.get_display_name(user_data)

        balance_message = message_formatter.format_balance_message(balance_data, username)
        keyboard = bot_keyboard.get_balance_keyboard(balance_data)

        await update.message.reply_text(
            balance_message,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=keyboard
        )

    async def show_history(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Показать историю"""
        user_data = user_data_extractor.extract_user_data(update)
        history_data = db.get_user_history(user_data['user_id'])
        history_message = message_formatter.format_history_message(history_data)

        await update.message.reply_text(
            history_message,
            parse_mode=ParseMode.MARKDOWN
        )

    async def show_examples(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Показать примеры"""
        keyboard = bot_keyboard.get_examples_keyboard()
        examples_text = "🎓 *Примеры задач:*\n\n" + "\n".join(
            f"{i + 1}. {example}" for i, example in enumerate(EXAMPLE_PROBLEMS[:3])
        )

        await update.message.reply_text(
            examples_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=keyboard
        )

    async def show_subscriptions(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Показать подписки"""
        keyboard = bot_keyboard.get_subscription_plans_keyboard()
        subscriptions_text = "💎 *Тарифы:*\n\n" + "\n".join(
            f"• {plan['name']} - {plan['price']}{plan['currency']}/мес"
            for plan in SUBSCRIPTION_PLANS.values()
        )

        await update.message.reply_text(
            subscriptions_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=keyboard
        )

    # Callback методы
    async def handle_solution_mode_callback(self, query, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Показать выбор режима из callback"""
        try:
            keyboard = bot_keyboard.get_solution_mode_keyboard()  # Правильное название метода
            if not keyboard:
                raise ValueError("Клавиатура режимов не создана")

            await query.edit_message_text(
                BOT_MESSAGES['mode_selection'],
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboard
            )
        except Exception as e:
            logger.error(f"Ошибка в handle_solution_mode_callback: {e}")
            await query.edit_message_text("❌ Ошибка выбора режима")

    async def show_main_menu_callback(self, query, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Показать главное меню из callback"""
        try:
            # Отправляем новое сообщение с reply-клавиатурой вместо редактирования
            await query.message.reply_text(
                "🏠 *Главное меню* - выберите действие:",
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=bot_keyboard.get_main_menu()
            )
            # Удаляем предыдущее сообщение с inline-клавиатурой
            await query.delete_message()
        except Exception as e:
            logger.error(f"Ошибка в show_main_menu_callback: {e}")
            await query.edit_message_text("❌ Ошибка отображения меню")

    async def show_balance_callback(self, query, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Показать баланс из callback"""
        try:
            # Правильно получаем user_data из callback query
            user_data = {
                'user_id': query.from_user.id,
                'username': query.from_user.username,
                'first_name': query.from_user.first_name,
                'last_name': query.from_user.last_name,
                'language_code': query.from_user.language_code or 'ru'
            }

            balance_data = db.get_user_balance(user_data['user_id'])
            username = user_data_extractor.get_display_name(user_data)

            balance_message = message_formatter.format_balance_message(balance_data, username)
            keyboard = bot_keyboard.get_balance_keyboard(balance_data)

            await query.edit_message_text(
                balance_message,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=keyboard
            )
        except Exception as e:
            logger.error(f"Ошибка в show_balance_callback: {e}")
            await query.edit_message_text("❌ Ошибка получения баланса")

    async def solve_example_problem(self, query, context: ContextTypes.DEFAULT_TYPE, callback_data: str) -> None:
        """Решить пример задачи"""
        try:
            example_index = int(callback_data.split('_')[1])
            if 0 <= example_index < len(EXAMPLE_PROBLEMS):
                problem_text = EXAMPLE_PROBLEMS[example_index]
                await query.edit_message_text(f"📝 Пример: {problem_text}")
        except Exception as e:
            logger.error(f"Ошибка решения примера: {e}")

    # В классе MathBot заменяем эти методы:

    async def balance_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик команды /balance"""
        await self.show_balance(update, context)

    async def history_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик команды /history"""
        await self.show_history(update, context)

    # НА:
    async def handle_balance_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик команды /balance"""
        await self.show_balance(update, context)

    async def handle_history_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Обработчик команды /history"""
        await self.show_history(update, context)

    def setup_handlers(self) -> None:
        """Настройка обработчиков"""
        if not self.application:
            return

        # Команды
        self.application.add_handler(CommandHandler("start", self.start_command))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("balance", self.handle_balance_command))
        self.application.add_handler(CommandHandler("history", self.handle_history_command))

        # Обработчик для математических задач ДО главного меню
        self.application.add_handler(MessageHandler(
            filters.TEXT & filters.Regex(r'[0-9+\-*/=xXyYzZ]'),  # Сначала ловим математику
            self.handle_text_problem
        ))

        # Главное меню - после математики
        self.application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            self.handle_main_menu
        ))

        # Фото
        self.application.add_handler(MessageHandler(
            filters.PHOTO,
            self.handle_photo_problem
        ))

        # Callback запросы
        self.application.add_handler(CallbackQueryHandler(self.handle_callback_query))

    def run(self):
        """Запуск бота"""
        try:
            self.application = Application.builder().token(self.token).build()
            self.setup_handlers()

            print("🤖 МатБот запущен!")
            print("📱 Используйте /start в Telegram")

            self.application.run_polling()

        except Exception as e:
            logger.error(f"Ошибка запуска: {e}")
            print(f"❌ Ошибка: {e}")


def main():
    """Главная функция"""
    if not TELEGRAM_TOKEN:
        raise ValueError("""
    ❌ TELEGRAM_TOKEN не найден!""")
    bot = MathBot(TELEGRAM_TOKEN)
    bot.run()


if __name__ == "__main__":
    main()
