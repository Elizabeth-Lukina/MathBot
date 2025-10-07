import sqlite3
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class Database:
    def __init__(self, db_path='math_bot.db'):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """Инициализация базы данных"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Таблица пользователей
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY,
                        username TEXT,
                        first_name TEXT,
                        last_name TEXT,
                        free_solutions INTEGER DEFAULT 3,
                        paid_solutions INTEGER DEFAULT 0,
                        total_problems_solved INTEGER DEFAULT 0,
                        registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')

                # Таблица решений
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS solutions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        problem_text TEXT,
                        solution_result TEXT,
                        problem_type TEXT,
                        processing_time REAL,
                        steps_count INTEGER DEFAULT 0,
                        image_path TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (user_id)
                    )
                ''')

                conn.commit()
                logger.info("База данных инициализирована")

        except Exception as e:
            logger.error(f"Ошибка инициализации БД: {e}")

    def create_user(self, user_id, username, first_name, last_name):
        """Создание пользователя"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute('''
                    INSERT OR IGNORE INTO users (user_id, username, first_name, last_name)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, username, first_name, last_name))

                conn.commit()
                logger.info(f"Создан пользователь {user_id}")

        except Exception as e:
            logger.error(f"Ошибка создания пользователя: {e}")

    def get_user(self, user_id):
        """Получение пользователя"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
                user = cursor.fetchone()
                return dict(user) if user else None

        except Exception as e:
            logger.error(f"Ошибка получения пользователя: {e}")
            return None

    def can_user_solve(self, user_id):
        """Проверка возможности решения"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute('''
                    SELECT 1 FROM users 
                    WHERE user_id = ? AND (free_solutions > 0 OR paid_solutions > 0)
                ''', (user_id,))

                return cursor.fetchone() is not None

        except Exception as e:
            logger.error(f"Ошибка проверки доступа: {e}")
            return False

    def use_solution(self, user_id):
        """Использование решения"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # Сначала используем платные решения
                cursor.execute('''
                    UPDATE users 
                    SET paid_solutions = paid_solutions - 1,
                        total_problems_solved = total_problems_solved + 1
                    WHERE user_id = ? AND paid_solutions > 0
                ''', (user_id,))

                if cursor.rowcount == 0:
                    # Используем бесплатные
                    cursor.execute('''
                        UPDATE users 
                        SET free_solutions = free_solutions - 1,
                            total_problems_solved = total_problems_solved + 1
                        WHERE user_id = ? AND free_solutions > 0
                    ''', (user_id,))

                conn.commit()
                return cursor.rowcount > 0

        except Exception as e:
            logger.error(f"Ошибка использования решения: {e}")
            return False

    def refund_solution(self, user_id):
        """Возврат решения"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute('''
                    UPDATE users 
                    SET free_solutions = free_solutions + 1
                    WHERE user_id = ?
                ''', (user_id,))

                conn.commit()
                return cursor.rowcount > 0

        except Exception as e:
            logger.error(f"Ошибка возврата решения: {e}")
            return False

    def save_solution(self, solution_data):
        """Сохранение решения"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                cursor.execute('''
                    INSERT INTO solutions 
                    (user_id, problem_text, solution_result, problem_type, processing_time, steps_count, image_path)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    solution_data['user_id'],
                    solution_data['problem_text'],
                    solution_data['solution_result'],
                    solution_data['problem_type'],
                    solution_data['processing_time'],
                    solution_data.get('steps_count', 0),
                    solution_data.get('image_path')
                ))

                conn.commit()
                logger.info(f"Сохранено решение для {solution_data['user_id']}")

        except Exception as e:
            logger.error(f"Ошибка сохранения решения: {e}")

    def get_user_history(self, user_id, limit=5):
        """Получение истории"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()

                cursor.execute('''
                    SELECT * FROM solutions 
                    WHERE user_id = ? 
                    ORDER BY created_at DESC 
                    LIMIT ?
                ''', (user_id, limit))

                return [dict(row) for row in cursor.fetchall()]

        except Exception as e:
            logger.error(f"Ошибка получения истории: {e}")
            return []


# Глобальный экземпляр
db = Database()