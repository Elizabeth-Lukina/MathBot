# -*- coding: utf-8 -*-
"""
Модуль для работы с базой данных SQLite
Управляет пользователями, историей решений, подписками и аналитикой
"""

import sqlite3
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from config import DATABASE_PATH, FREE_SOLUTIONS_FOR_NEW_USERS

logger = logging.getLogger(__name__)

class Database:
    """Класс для работы с базой данных бота"""
    
    def __init__(self, db_path: str = DATABASE_PATH):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Инициализация базы данных и создание таблиц"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Таблица пользователей
                cursor.execute(f'''
                    CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY,
                        username TEXT,
                        first_name TEXT,
                        last_name TEXT,
                        language_code TEXT DEFAULT 'ru',
                        registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        free_solutions INTEGER DEFAULT {FREE_SOLUTIONS_FOR_NEW_USERS},
                        paid_solutions INTEGER DEFAULT 0,
                        subscription_type TEXT DEFAULT NULL,
                        subscription_end TIMESTAMP DEFAULT NULL,
                        total_problems_solved INTEGER DEFAULT 0,
                        is_active BOOLEAN DEFAULT 1
                    )
                ''')
                
                # Таблица истории решений
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS solutions_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        problem_text TEXT NOT NULL,
                        problem_type TEXT,
                        solution_method TEXT,  -- 'sympy' или 'openai'
                        solution_result TEXT,
                        explanation TEXT,
                        latex_formatted TEXT,
                        image_path TEXT DEFAULT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        processing_time REAL,
                        success BOOLEAN DEFAULT 1,
                        FOREIGN KEY (user_id) REFERENCES users (user_id)
                    )
                ''')
                
                # Таблица платежей и подписок
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS payments (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        payment_type TEXT,  -- 'subscription' или 'package'
                        package_type TEXT,
                        amount REAL,
                        currency TEXT DEFAULT 'RUB',
                        payment_status TEXT DEFAULT 'pending',
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        processed_at TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (user_id)
                    )
                ''')
                
                # Таблица статистики использования
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS usage_stats (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        date DATE DEFAULT CURRENT_DATE,
                        total_users INTEGER DEFAULT 0,
                        active_users INTEGER DEFAULT 0,
                        problems_solved INTEGER DEFAULT 0,
                        sympy_solutions INTEGER DEFAULT 0,
                        openai_solutions INTEGER DEFAULT 0,
                        photos_processed INTEGER DEFAULT 0,
                        new_registrations INTEGER DEFAULT 0,
                        openai_cost REAL DEFAULT 0.0,
                        UNIQUE(date)
                    )
                ''')
                
                # Таблица для реферальной программы
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS referrals (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        referrer_id INTEGER,
                        referred_id INTEGER,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        bonus_given BOOLEAN DEFAULT 0,
                        FOREIGN KEY (referrer_id) REFERENCES users (user_id),
                        FOREIGN KEY (referred_id) REFERENCES users (user_id)
                    )
                ''')
                
                conn.commit()
                logger.info("База данных успешно инициализирована")
                
        except Exception as e:
            logger.error(f"Ошибка инициализации базы данных: {e}")
    
    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Получить информацию о пользователе"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
                row = cursor.fetchone()
                
                if row:
                    return dict(row)
                return None
                
        except Exception as e:
            logger.error(f"Ошибка получения пользователя {user_id}: {e}")
            return None
    
    def create_or_update_user(self, user_data: Dict[str, Any]) -> bool:
        """Создать или обновить пользователя"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Проверяем, существует ли пользователь
                existing_user = self.get_user(user_data['user_id'])
                
                if existing_user:
                    # Обновляем данные существующего пользователя
                    cursor.execute('''
                        UPDATE users 
                        SET username = ?, first_name = ?, last_name = ?, 
                            language_code = ?, last_activity = CURRENT_TIMESTAMP
                        WHERE user_id = ?
                    ''', (
                        user_data.get('username'),
                        user_data.get('first_name'),
                        user_data.get('last_name'),
                        user_data.get('language_code', 'ru'),
                        user_data['user_id']
                    ))
                else:
                    # Создаем нового пользователя
                    cursor.execute('''
                        INSERT INTO users (user_id, username, first_name, last_name, language_code)
                        VALUES (?, ?, ?, ?, ?)
                    ''', (
                        user_data['user_id'],
                        user_data.get('username'),
                        user_data.get('first_name'),
                        user_data.get('last_name'),
                        user_data.get('language_code', 'ru')
                    ))
                    
                    # Обновляем статистику новых регистраций
                    self.update_daily_stats('new_registrations', 1)
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"Ошибка создания/обновления пользователя: {e}")
            return False
    
    def get_user_balance(self, user_id: int) -> Dict[str, Any]:
        """Получить баланс пользователя"""
        user = self.get_user(user_id)
        if not user:
            return {'free_solutions': 0, 'paid_solutions': 0, 'subscription': None}
        
        # Проверяем активность подписки
        subscription_active = False
        if user['subscription_end']:
            subscription_end = datetime.fromisoformat(user['subscription_end'])
            subscription_active = subscription_end > datetime.now()
        
        return {
            'free_solutions': user['free_solutions'],
            'paid_solutions': user['paid_solutions'],
            'subscription': {
                'type': user['subscription_type'],
                'active': subscription_active,
                'end_date': user['subscription_end']
            }
        }
    
    def use_solution(self, user_id: int) -> bool:
        """Использовать одно решение из баланса пользователя"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                user = self.get_user(user_id)
                if not user:
                    return False
                
                # Проверяем подписку
                subscription_active = False
                if user['subscription_end']:
                    subscription_end = datetime.fromisoformat(user['subscription_end'])
                    subscription_active = subscription_end > datetime.now()
                
                if subscription_active:
                    # У пользователя активная подписка - решения не списываем
                    return True
                
                # Списываем сначала бесплатные, потом платные решения
                if user['free_solutions'] > 0:
                    cursor.execute('''
                        UPDATE users SET free_solutions = free_solutions - 1,
                        total_problems_solved = total_problems_solved + 1
                        WHERE user_id = ?
                    ''', (user_id,))
                elif user['paid_solutions'] > 0:
                    cursor.execute('''
                        UPDATE users SET paid_solutions = paid_solutions - 1,
                        total_problems_solved = total_problems_solved + 1
                        WHERE user_id = ?
                    ''', (user_id,))
                else:
                    # Нет доступных решений
                    return False
                
                conn.commit()
                return True
                
        except Exception as e:
            logger.error(f"Ошибка использования решения для пользователя {user_id}: {e}")
            return False
    
    def save_solution(self, solution_data: Dict[str, Any]) -> bool:
        """Сохранить решение в историю"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute('''
                    INSERT INTO solutions_history 
                    (user_id, problem_text, problem_type, solution_method, 
                     solution_result, explanation, latex_formatted, image_path, 
                     processing_time, success)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    solution_data['user_id'],
                    solution_data['problem_text'],
                    solution_data.get('problem_type'),
                    solution_data.get('solution_method'),
                    solution_data.get('solution_result'),
                    solution_data.get('explanation'),
                    solution_data.get('latex_formatted'),
                    solution_data.get('image_path'),
                    solution_data.get('processing_time'),
                    solution_data.get('success', True)
                ))
                
                conn.commit()
                
                # Обновляем статистику
                method = solution_data.get('solution_method', 'unknown')
                if method == 'sympy':
                    self.update_daily_stats('sympy_solutions', 1)
                elif method == 'openai':
                    self.update_daily_stats('openai_solutions', 1)
                
                self.update_daily_stats('problems_solved', 1)
                
                return True
                
        except Exception as e:
            logger.error(f"Ошибка сохранения решения: {e}")
            return False
    
    def get_user_history(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Получить историю решений пользователя"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                cursor.execute('''
                    SELECT * FROM solutions_history 
                    WHERE user_id = ? AND success = 1
                    ORDER BY created_at DESC 
                    LIMIT ?
                ''', (user_id, limit))
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
                
        except Exception as e:
            logger.error(f"Ошибка получения истории пользователя {user_id}: {e}")
            return []
    
    def update_daily_stats(self, stat_name: str, increment: int = 1):
        """Обновить ежедневную статистику"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                today = datetime.now().date()
                
                # Создаем запись на сегодня, если её нет
                cursor.execute('''
                    INSERT OR IGNORE INTO usage_stats (date) VALUES (?)
                ''', (str(today),))
                
                # Обновляем статистику (используем безопасный способ)
                if stat_name in ['total_users', 'active_users', 'problems_solved', 'sympy_solutions', 
                               'openai_solutions', 'photos_processed', 'new_registrations', 'openai_cost']:
                    if stat_name == 'openai_cost':
                        cursor.execute(f'''
                            UPDATE usage_stats 
                            SET {stat_name} = {stat_name} + ? 
                            WHERE date = ?
                        ''', (float(increment), str(today)))
                    else:
                        cursor.execute(f'''
                            UPDATE usage_stats 
                            SET {stat_name} = {stat_name} + ? 
                            WHERE date = ?
                        ''', (int(increment), str(today)))
                
                conn.commit()
                
        except Exception as e:
            logger.error(f"Ошибка обновления статистики {stat_name}: {e}")
    
    def get_daily_stats(self, days: int = 7) -> List[Dict[str, Any]]:
        """Получить статистику за последние дни"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                
                start_date = datetime.now().date() - timedelta(days=days)
                
                cursor.execute('''
                    SELECT * FROM usage_stats 
                    WHERE date >= ? 
                    ORDER BY date DESC
                ''', (start_date,))
                
                rows = cursor.fetchall()
                return [dict(row) for row in rows]
                
        except Exception as e:
            logger.error(f"Ошибка получения статистики: {e}")
            return []
    
    def backup_database(self, backup_path: str = None) -> bool:
        """Создать резервную копию базы данных"""
        try:
            if not backup_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = f"backup_mathbot_{timestamp}.db"
            
            # Простое копирование файла базы данных
            import shutil
            shutil.copy2(self.db_path, backup_path)
            
            logger.info(f"Резервная копия создана: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"Ошибка создания резервной копии: {e}")
            return False

# Создаем глобальный экземпляр базы данных
db = Database()