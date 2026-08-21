"""
Решатель производных
"""

import sympy as sp
import logging
import re
from typing import Dict, Any
from sympy import symbols, diff, parse_expr, simplify

logger = logging.getLogger(__name__)


class DerivativeSolver:
    """Класс для вычисления производных математических выражений"""

    def solve(self, text: str) -> Dict[str, Any]:
        """
        Основной метод для решения производных

        Args:
            text: Текст с математическим выражением для дифференцирования

        Returns:
            Словарь с результатом вычисления производной
        """
        try:
            logger.info(f"Обрабатываем производную: {text}")

            # Извлекаем математическое выражение из текста
            expression = self._extract_expression(text)

            if not expression:
                return self._create_error_response('Не найдено выражение для дифференцирования')

            # Нормализуем выражение для корректного парсинга
            normalized_expression = self._normalize_expression(expression)
            logger.info(f"Нормализованное выражение: {normalized_expression}")

            # Парсим выражение с помощью SymPy
            expr = self._parse_expression(normalized_expression)
            if not expr:
                return self._create_error_response('Ошибка парсинга выражения')

            # Проверяем наличие переменных для дифференцирования
            variables = expr.free_symbols
            if not variables:
                return self._create_error_response('Нет переменных для дифференцирования')

            # Вычисляем производную
            var = list(variables)[0]
            derivative = diff(expr, var)

            # Формируем шаги решения для пользователя
            steps = self._generate_solution_steps(expr, derivative, var)

            return {
                'success': True,
                'solution': f"f'({var}) = {derivative}",
                'steps': steps,
                'latex': f"{sp.latex(derivative)}",
                'explanation': "Производная функции найдена успешно"
            }

        except Exception as e:
            logger.error(f"Ошибка вычисления производной: {e}")
            return self._create_error_response(f'Ошибка вычисления: {e}')

    def _extract_expression(self, text: str) -> str:
        """
        Извлекает математическое выражение из текста пользователя
        """
        logger.debug(f"Извлекаем выражение из текста: '{text}'")

        # 1. Ищем f(x) = выражение (высший приоритет)
        match_fx = re.search(r'f\s*\(\s*x\s*\)\s*=\s*(.+)', text, re.IGNORECASE)
        if match_fx:
            expression = match_fx.group(1).strip()
            logger.debug(f"Извлекли из f(x): '{expression}'")
            return expression

        # 2. Ищем производную от выражения
        match_deriv = re.search(r'производная\s+(?:от\s+)?(.+)', text.lower())
        if match_deriv:
            expression = match_deriv.group(1).strip()
            # Убираем "по x" если есть
            expression = re.sub(r'\s*по\s*x\s*$', '', expression)
            logger.debug(f"Извлекли из 'производная от': '{expression}'")
            return expression

        # 3. Ищем "найти производную"
        match_find = re.search(r'найти\s+производную\s+(.+)', text.lower())
        if match_find:
            expression = match_find.group(1).strip()
            logger.debug(f"Извлекли из 'найти производную': '{expression}'")
            return expression

        # 4. Удаляем русские команды и оставляем только математику
        clean_text = self._remove_derivative_commands(text)
        logger.debug(f"Очищенный текст: '{clean_text}'")

        # 5. Ищем математическое выражение
        math_expression = self._find_math_expression(clean_text)
        if math_expression:
            logger.debug(f"Извлекли математическое выражение: '{math_expression}'")
            return math_expression

        logger.debug("Не удалось извлечь выражение")
        return None

    def _remove_derivative_commands(self, text: str) -> str:
        """Удаляет команды связанные с производными из текста"""
        derivative_commands = [
            'производная', 'производную', 'найти', 'функции', 'функция',
            'от', 'дифференцировать', 'дифференциал', r'f\'\s*\(\s*x\s*\)'
        ]

        clean_text = text
        for command in derivative_commands:
            clean_text = re.sub(command, '', clean_text, flags=re.IGNORECASE)

        return clean_text.strip()

    def _find_math_expression(self, text: str) -> str:
        """Находит математическое выражение в тексте"""
        # Паттерн для математических выражений
        math_pattern = r'([a-zA-Z\d+\-*/\^\.\s\(\)e]+)'
        matches = re.findall(math_pattern, text)

        if matches:
            # Берем самое длинное математическое выражение
            expression = max(matches, key=len).strip()
            expression = re.sub(r'\s+', ' ', expression)
            return expression

        return None

    def _normalize_expression(self, expression: str) -> str:
        """
        Нормализует математическое выражение для SymPy
        """
        if not expression:
            return expression

        # Импортируем общий нормализатор
        from .expression_normalizer import expression_normalizer

        # Используем общую нормализацию
        normalized = expression_normalizer.normalize_expression(expression)

        return normalized

    def _parse_expression(self, expression: str):
        """Парсит математическое выражение с обработкой ошибок"""
        try:
            return parse_expr(expression)
        except Exception as e:
            logger.error(f"Ошибка парсинга выражения '{expression}': {e}")
            return None

    def _generate_solution_steps(self, expr, derivative, var) -> list:
        """
        Генерирует шаги решения для отображения пользователю
        """
        steps = [
            f"Функция: f({var}) = {sp.latex(expr)}",
            f"Производная: f'({var}) = {sp.latex(derivative)}"
        ]

        # Добавляем правило дифференцирования для сложных выражений
        rule = self._identify_differentiation_rule(expr)
        if rule:
            steps.insert(1, f"Применено правило: {rule}")

        return steps

    def _identify_differentiation_rule(self, expr) -> str:
        """Определяет какое правило дифференцирования было применено"""
        expr_str = str(expr)

        if '*' in expr_str and '(' in expr_str:
            return "произведения (uv)' = u'v + uv'"
        elif '/' in expr_str:
            return "частного (u/v)' = (u'v - uv')/v²"
        elif '**' in expr_str or '^' in expr_str:
            return "степенной функции"
        elif any(func in expr_str for func in ['sin', 'cos', 'tan']):
            return "тригонометрических функций"
        elif 'exp' in expr_str or 'log' in expr_str:
            return "экспоненциальных или логарифмических функций"
        else:
            return None

    def _create_error_response(self, message: str) -> Dict[str, Any]:
        """Создает стандартизированный ответ с ошибкой"""
        return {
            'success': False,
            'solution': '',
            'steps': [],
            'latex': '',
            'explanation': message
        }



derivative_solver = DerivativeSolver()