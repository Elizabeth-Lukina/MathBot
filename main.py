import telebot
import logging
import os
import traceback
from telebot import types

from config import logger, TELEGRAM_TOKEN
from database import db
from math_solver import math_solver
from image_processor import image_processor
from keyboard import bot_keyboard

# Инициализация бота
try:
    bot = telebot.TeleBot(TELEGRAM_TOKEN)
    logger.info("Бот инициализирован успешно")
except Exception as e:
    logger.error(f"Ошибка инициализации бота: {e}")
    exit(1)


def format_step_by_step_response(solution, problem_text):
    """Форматирование ответа с шагами"""
    try:
        response_text = f"""
✅ <b>Задача решена!</b>

📝 <b>Задача:</b>
<code>{problem_text[:100]}{'...' if len(problem_text) > 100 else ''}</code>

🧮 <b>Тип:</b> {solution['problem_type']}
⏱ <b>Время:</b> {solution['processing_time']:.1f} сек
🎯 <b>Ответ:</b> <code>{solution['solution']}</code>

📋 <b>Пошаговое решение:</b>
"""

        for i, step in enumerate(solution.get('steps', [])[:5], 1):
            response_text += f"\n{i}. {step.get('description', 'Шаг')}"
            if 'formula' in step:
                response_text += f"\n   📐 <code>{step['formula']}</code>"

        if solution.get('method_explanation'):
            response_text += f"\n\n💡 <b>Метод решения:</b>\n{solution['method_explanation']}"

        return response_text

    except Exception as e:
        logger.error(f"Ошибка форматирования ответа: {e}")
        return "❌ Ошибка форматирования ответа"


@bot.message_handler(commands=['start'])
def handle_start(message):
    """Обработчик /start"""
    try:
        logger.info(f"Команда /start от пользователя {message.from_user.id}")

        user_id = message.from_user.id
        username = message.from_user.username
        first_name = message.from_user.first_name
        last_name = message.from_user.last_name

        # Создаем пользователя если не существует
        db.create_user(user_id, username, first_name, last_name)

        welcome_text = f"""
👋 <b>Добро пожаловать, {first_name}!</b>

🤖 <b>MathBot Premium</b> - твой личный математический помощник!

✨ <b>Что я умею:</b>
• Решать уравнения и системы
• Находить производные и интегралы
• Упрощать выражения
• Работать с тригонометрией
• Распознавать задачи с фото

🎁 <b>Бесплатно:</b> {db.get_user(user_id)['free_solutions']} решений

Выберите действие:
        """

        bot.send_message(
            message.chat.id,
            welcome_text,
            parse_mode='HTML',
            reply_markup=bot_keyboard.main_menu()
        )

    except Exception as e:
        logger.error(f"Ошибка в /start: {e}\n{traceback.format_exc()}")


@bot.message_handler(func=lambda message: message.text == "🎯 Решить задачу")
def handle_solve_problem(message):
    """Обработчик кнопки Решить задачу"""
    try:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📝 Текст", callback_data="input_text"))
        markup.add(types.InlineKeyboardButton("📸 Фото", callback_data="input_photo"))

        bot.send_message(
            message.chat.id,
            "📝 <b>Выберите способ ввода задачи:</b>",
            parse_mode='HTML',
            reply_markup=markup
        )
    except Exception as e:
        logger.error(f"Ошибка в handle_solve_problem: {e}")


@bot.message_handler(func=lambda message: message.text == "💰 Мой баланс")
def handle_balance(message):
    """Обработчик кнопки Мой баланс"""
    try:
        user = db.get_user(message.from_user.id)
        if user:
            balance_text = f"""
💼 <b>Ваш баланс:</b>

🎁 Бесплатные решения: {user['free_solutions']}
💳 Платные решения: {user['paid_solutions']}
📊 Всего решено: {user['total_problems_solved']}
            """

            bot.send_message(
                message.chat.id,
                balance_text,
                parse_mode='HTML'
            )
    except Exception as e:
        logger.error(f"Ошибка в handle_balance: {e}")


@bot.message_handler(func=lambda message: message.text == "💳 Купить решения")
def handle_buy_solutions(message):
    """Обработчик кнопки Купить решения"""
    try:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("🔔 Подписки", callback_data="buy_subscription"))
        markup.add(types.InlineKeyboardButton("📦 Пакеты решений", callback_data="buy_package"))

        bot.send_message(
            message.chat.id,
            "🛒 <b>Выберите тип покупки:</b>",
            parse_mode='HTML',
            reply_markup=markup
        )
    except Exception as e:
        logger.error(f"Ошибка в handle_buy_solutions: {e}")


@bot.message_handler(func=lambda message: message.text == "📊 История")
def handle_history(message):
    """Обработчик кнопки История"""
    try:
        history = db.get_user_history(message.from_user.id)
        if history:
            history_text = "📊 <b>Последние решения:</b>\n\n"
            for i, item in enumerate(history, 1):
                history_text += f"{i}. {item['problem_text'][:50]}...\n"
        else:
            history_text = "📝 История решений пуста"

        bot.send_message(
            message.chat.id,
            history_text,
            parse_mode='HTML'
        )
    except Exception as e:
        logger.error(f"Ошибка в handle_history: {e}")


@bot.message_handler(func=lambda message: message.text == "🆘 Помощь")
def handle_help(message):
    """Обработчик кнопки Помощь"""
    try:
        help_text = """
🆘 <b>Помощь по боту:</b>

📝 <b>Как отправить задачу:</b>
• Напишите текст задачи
• Или отправьте фото с задачей

🧮 <b>Поддерживаемые типы задач:</b>
• Уравнения и системы
• Производные и интегралы
• Тригонометрические выражения
• Арифметические вычисления

💳 <b>Оплата и подписки:</b>
• Бесплатно: 3 решения
• Пакеты: 10/25/50 решений
• Подписки: Базовая/Премиум

📞 <b>Поддержка:</b> @username
        """

        bot.send_message(
            message.chat.id,
            help_text,
            parse_mode='HTML'
        )
    except Exception as e:
        logger.error(f"Ошибка в handle_help: {e}")


@bot.message_handler(content_types=['text'])
def handle_text_messages(message):
    """Обработка текстовых сообщений"""
    try:
        logger.info(f"Текстовое сообщение от {message.from_user.id}: {message.text[:50]}...")

        user_id = message.from_user.id
        problem_text = message.text

        # Проверяем возможность решения
        if not db.can_user_solve(user_id):
            logger.warning(f"У пользователя {user_id} закончились решения")
            bot.send_message(
                message.chat.id,
                "❌ <b>Закончились бесплатные решения!</b>\n\n"
                "💳 Купите пакет решений или подписку",
                parse_mode='HTML',
                reply_markup=bot_keyboard.buy_menu()
            )
            return

        # Используем решение
        if not db.use_solution(user_id):
            logger.error(f"Ошибка использования решения у пользователя {user_id}")
            bot.send_message(
                message.chat.id,
                "❌ <b>Ошибка использования решения</b>",
                parse_mode='HTML'
            )
            return

        processing_msg = bot.send_message(
            message.chat.id,
            "🧠 <b>Решаю задачу...</b>",
            parse_mode='HTML'
        )

        # Решаем задачу
        logger.debug(f"Передаем задачу решателю: {problem_text}")
        solution = math_solver.solve_with_steps(problem_text)
        logger.debug(f"Результат решения: {solution}")

        if solution['success']:
            # Сохраняем и отправляем ответ
            db.save_solution({
                'user_id': user_id,
                'problem_text': problem_text,
                'solution_result': str(solution['solution']),
                'problem_type': solution.get('problem_type', 'unknown'),
                'processing_time': solution.get('processing_time', 0),
                'steps_count': len(solution.get('steps', []))
            })

            response_text = format_step_by_step_response(solution, problem_text)

            bot.edit_message_text(
                response_text,
                message.chat.id,
                processing_msg.message_id,
                parse_mode='HTML'
            )

        else:
            # Возвращаем решение
            db.refund_solution(user_id)
            error_msg = "❌ <b>Не удалось решить задачу</b>"
            if 'error' in solution:
                error_msg += f"\n\nОшибка: {solution['error']}"
                logger.warning(f"Ошибка решения: {solution['error']}")

            bot.edit_message_text(
                error_msg,
                message.chat.id,
                processing_msg.message_id,
                parse_mode='HTML'
            )

    except Exception as e:
        logger.error(f"Критическая ошибка в handle_text_messages: {e}\n{traceback.format_exc()}")
        bot.send_message(
            message.chat.id,
            "❌ <b>Произошла критическая ошибка</b>\n\nПопробуйте еще раз или обратитесь в поддержку",
            parse_mode='HTML'
        )


@bot.message_handler(content_types=['photo'])
def handle_photos(message):
    """Обработка фотографий"""
    try:
        logger.info(f"Фото от пользователя {message.from_user.id}")

        # Проверяем возможность решения
        if not db.can_user_solve(message.from_user.id):
            bot.send_message(
                message.chat.id,
                "❌ <b>Закончились бесплатные решения!</b>",
                parse_mode='HTML',
                reply_markup=bot_keyboard.buy_menu()
            )
            return

        # Скачиваем фото
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        # Обрабатываем изображение
        processing_msg = bot.send_message(
            message.chat.id,
            "🔍 <b>Распознаю текст с фото...</b>",
            parse_mode='HTML'
        )

        recognized_text = image_processor.process_image(downloaded_file)

        if not recognized_text or not image_processor.is_mathematical(recognized_text):
            bot.edit_message_text(
                "❌ <b>Не удалось распознать математическую задачу</b>\n\n"
                "Попробуйте отправить более четкое фото или введите текст вручную",
                message.chat.id,
                processing_msg.message_id,
                parse_mode='HTML'
            )
            return

        # Используем решение
        if not db.use_solution(message.from_user.id):
            bot.edit_message_text(
                "❌ <b>Ошибка использования решения</b>",
                message.chat.id,
                processing_msg.message_id,
                parse_mode='HTML'
            )
            return

        # Решаем задачу
        bot.edit_message_text(
            "🧠 <b>Решаю задачу...</b>",
            message.chat.id,
            processing_msg.message_id,
            parse_mode='HTML'
        )

        solution = math_solver.solve_with_steps(recognized_text)

        if solution['success']:
            # Сохраняем решение
            db.save_solution({
                'user_id': message.from_user.id,
                'problem_text': recognized_text,
                'solution_result': str(solution['solution']),
                'problem_type': solution.get('problem_type', 'unknown'),
                'processing_time': solution.get('processing_time', 0),
                'steps_count': len(solution.get('steps', [])),
                'image_path': file_info.file_path
            })

            response_text = f"📸 <b>Распознанный текст:</b>\n<code>{recognized_text[:100]}...</code>\n\n"
            response_text += format_step_by_step_response(solution, recognized_text)

            bot.edit_message_text(
                response_text,
                message.chat.id,
                processing_msg.message_id,
                parse_mode='HTML'
            )

        else:
            # Возвращаем решение
            db.refund_solution(message.from_user.id)
            error_msg = "❌ <b>Не удалось решить задачу</b>"
            if 'error' in solution:
                error_msg += f"\n\nОшибка: {solution['error']}"

            bot.edit_message_text(
                error_msg,
                message.chat.id,
                processing_msg.message_id,
                parse_mode='HTML'
            )

    except Exception as e:
        logger.error(f"Ошибка обработки фото: {e}\n{traceback.format_exc()}")
        bot.send_message(
            message.chat.id,
            "❌ <b>Ошибка обработки фото</b>",
            parse_mode='HTML'
        )


@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    """Обработка callback-запросов"""
    try:
        if call.data == "input_text":
            bot.send_message(
                call.message.chat.id,
                "📝 <b>Введите текст задачи:</b>",
                parse_mode='HTML'
            )
        elif call.data == "input_photo":
            bot.send_message(
                call.message.chat.id,
                "📸 <b>Отправьте фото с задачей:</b>",
                parse_mode='HTML'
            )
        elif call.data == "solve_another":
            handle_solve_problem(call.message)
        elif call.data == "buy_more":
            handle_buy_solutions(call.message)

    except Exception as e:
        logger.error(f"Ошибка в callback: {e}")


def run_bot():
    """Запуск бота с обработкой исключений"""
    try:
        logger.info("Запуск MathBot Premium...")
        print("🚀 Бот запускается...")
        print("📋 Логи пишутся в папку debug_logs/")

        bot.polling(none_stop=True, interval=0, timeout=60)

    except Exception as e:
        logger.critical(f"Критическая ошибка запуска бота: {e}\n{traceback.format_exc()}")
        print(f"❌ Критическая ошибка: {e}")


if __name__ == "__main__":
    # Создаем папку для логов
    os.makedirs('debug_logs', exist_ok=True)
    run_bot()