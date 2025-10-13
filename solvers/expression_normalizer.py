"""
Нормализатор математических выражений
"""

import re
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)


class ExpressionNormalizer:
    """Класс для нормализации математических выражений"""

    @staticmethod
    def normalize_expression(text: str) -> str:
        """Основная функция нормализации математических выражений"""
        if not text:
            return text

        # Удаляем русские команды
        clean_text = ExpressionNormalizer._remove_russian_commands(text)

        # Заменяем специальные символы
        normalized = ExpressionNormalizer._replace_special_symbols(clean_text)

        # Добавляем операторы умножения
        normalized = ExpressionNormalizer._add_multiplication_operators(normalized)

        # Обрабатываем экспоненциальные выражения
        normalized = ExpressionNormalizer._process_exponential_expressions(normalized)

        # Нормализуем математические функции
        normalized = ExpressionNormalizer._normalize_math_functions(normalized)

        # Убираем лишние пробелы
        normalized = re.sub(r'\s+', '', normalized)

        logger.info(f"Нормализованное выражение: {normalized}")
        return normalized

    @staticmethod
    def normalize_equation(text: str) -> str:
        """Нормализация уравнений"""
        # Удаляем русские слова
        clean_text = ExpressionNormalizer._remove_russian_words(text)

        # Заменяем ^ на **
        normalized = clean_text.replace('^', '**')

        return normalized

    @staticmethod
    def normalize_mathematical_text(text: str) -> str:
        """Нормализация математического текста с функциями"""
        replacements = {
            'син': 'sin', 'кос': 'cos', 'тан': 'tan', 'тг': 'tan',
            'котан': 'cot', 'ктг': 'cot', 'пи': 'pi', '°': '',
            'градус': '', 'градусов': '', 'корень': 'sqrt', 'е': 'e'
        }

        text_normalized = text
        for russian, english in replacements.items():
            text_normalized = re.sub(russian, english, text_normalized, flags=re.IGNORECASE)

        text_normalized = text_normalized.replace('π', 'pi')
        text_normalized = text_normalized.replace('^', '**')

        # Заменяем градусы на радианы
        degree_pattern = r'(\d+)\s*°'
        text_normalized = re.sub(degree_pattern, r'(\1*pi/180)', text_normalized)

        return text_normalized.strip()

    @staticmethod
    def clean_arithmetic_text(text: str) -> str:
        """Очистка арифметического текста"""
        # Убираем лишние пробелы
        text = ' '.join(text.split())
        # Заменяем запятые на точки для десятичных чисел
        text = re.sub(r'(\d),(\d)', r'\1.\2', text)
        return text.strip()

    @staticmethod
    def _remove_russian_commands(text: str) -> str:
        """Удаляет русские команды из текста"""
        commands = [
            'упростить', 'разложить', 'раскрыть', 'решить', 'производная',
            'производную', 'найти', 'функции', 'функция', 'от',
            'дифференцировать', 'дифференциал', 'интеграл', 'проинтегрировать',
            'вычислить', 'значение', 'выражение', 'тождество', 'доказать'
        ]

        clean_text = text
        for command in commands:
            clean_text = re.sub(command, '', clean_text, flags=re.IGNORECASE)

        return clean_text.strip()

    @staticmethod
    def _remove_russian_words(text: str) -> str:
        """Удаляет русские слова из текста"""
        russian_words = ['решить', 'уравнение', 'найти', 'вычислить', 'пример']
        clean_text = text
        for word in russian_words:
            clean_text = re.sub(word, '', clean_text, flags=re.IGNORECASE)
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        return clean_text

    @staticmethod
    def _replace_special_symbols(text: str) -> str:
        """Заменяет специальные символы"""
        replacements = {
            '²': '**2', '³': '**3', 'π': 'pi', '^': '**'
        }

        normalized = text
        for symbol, replacement in replacements.items():
            normalized = normalized.replace(symbol, replacement)

        return normalized

    @staticmethod
    def _add_multiplication_operators(text: str) -> str:
        """Добавляет операторы умножения где нужно"""
        normalized = text

        # Добавляем * между цифрой и буквой: 3x -> 3*x, 2sin(x) -> 2*sin(x)
        normalized = re.sub(r'(\d)([a-zA-Z\(])', r'\1*\2', normalized)

        # Добавляем * между буквой и цифрой: x2 -> x*2
        normalized = re.sub(r'([a-zA-Z\)])(\d)', r'\1*\2', normalized)

        # Добавляем * между ) и ( или буквой: )( -> )*(, )x -> )*x
        normalized = re.sub(r'(\))(\()', r'\1*\2', normalized)
        normalized = re.sub(r'(\))([a-zA-Z])', r'\1*\2', normalized)

        return normalized

    @staticmethod
    def _process_exponential_expressions(text: str) -> str:
        """Обрабатывает экспоненциальные выражения"""
        normalized = text

        # Обрабатываем e^x -> exp(x)
        patterns = [
            (r'e\^\(([^\)]+)\)', r'exp(\1)'),
            (r'e\^([^\(\)\s]+)', r'exp(\1)'),
            (r'e\*\*\(([^\)]+)\)', r'exp(\1)'),
            (r'e\*\*([^\(\)\s]+)', r'exp(\1)')
        ]

        for pattern, replacement in patterns:
            normalized = re.sub(pattern, replacement, normalized)

        return normalized

    @staticmethod
    def _normalize_math_functions(text: str) -> str:
        """Нормализует математические функции"""
        normalized = text

        # Заменяем ln на log
        normalized = re.sub(r'\bln\b', 'log', normalized)

        # Заменяем арктангенс
        normalized = re.sub(r'\barctan\b', 'atan', normalized)

        return normalized

    @staticmethod
    def extract_math_expression(text: str) -> str:
        """Извлекает математическое выражение из текста"""
        # Убираем слова команд
        clean_text = ExpressionNormalizer._remove_russian_commands(text)

        # Нормализуем
        normalized = ExpressionNormalizer.normalize_expression(clean_text)

        return normalized

    @staticmethod
    def normalize_limit(limit_str: str) -> str:
        """Нормализует предел интегрирования"""
        normalized = limit_str.replace('π', 'pi')

        if '/' in normalized and not re.search(r'[a-zA-Z]', normalized):
            parts = normalized.split('/')
            if len(parts) == 2:
                return f"({parts[0]})/({parts[1]})"

        return normalized


# Глобальный экземпляр
expression_normalizer = ExpressionNormalizer()

