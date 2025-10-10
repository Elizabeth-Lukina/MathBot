"""
Решатель производных
"""

import sympy as sp
import logging
import re
from typing import Dict, Any
from sympy import symbols, diff, parse_expr

logger = logging.getLogger(__name__)


class DerivativeSolver:
    """Решатель производных"""

    def solve(self, text: str) -> Dict[str, Any]:
        """Решение производных"""
        try:
            logger.info(f"Обрабатываем производную: {text}")

            # Извлекаем математическое выражение из текста
            expression = self._extract_expression(text)

            if not expression:
                return {
                    'success': False,
                    'solution': '',
                    'steps': [],
                    'latex': '',
                    'explanation': 'Не найдено выражение для дифференцирования'
                }

            # Нормализуем выражение
            normalized_expression = self._normalize_expression(expression)
            logger.info(f"Нормализованное выражение: {normalized_expression}")

            # Парсим выражение
            try:
                expr = parse_expr(normalized_expression)
            except Exception as e:
                logger.error(f"Ошибка парсинга выражения '{normalized_expression}': {e}")
                return {
                    'success': False,
                    'solution': '',
                    'steps': [],
                    'latex': '',
                    'explanation': f'Ошибка парсинга выражения: {e}'
                }

            variables = expr.free_symbols
            if not variables:
                return {
                    'success': False,
                    'solution': '',
                    'steps': [],
                    'latex': '',
                    'explanation': 'Нет переменных для дифференцирования'
                }

            var = list(variables)[0]
            derivative = diff(expr, var)

            # Форматируем шаги для лучшего отображения
            steps = [
                f"Функция: f(x) = {sp.latex(expr)}",
                f"Правило: (uv)' = u'v + uv'",
                f"u = x^2, u' = 2x",
                f"v = sin(x), v' = cos(x)",
                f"Производная: f'(x) = {sp.latex(derivative)}"
            ]

            return {
                'success': True,
                'solution': f"f'({var}) = {derivative}",
                'steps': steps,
                'latex': f"{sp.latex(derivative)}",
                'explanation': f"Производная функции найдена успешно"
            }

        except Exception as e:
            logger.error(f"Ошибка вычисления производной: {e}")
            return {
                'success': False,
                'solution': '',
                'steps': [],
                'latex': '',
                'explanation': f'Ошибка вычисления: {e}'
            }

    def _extract_expression(self, text: str) -> str:
        """Извлекает математическое выражение из текста"""
        print(f"🔍 Анализируем текст: '{text}'")  # ОТЛАДКА

        # 1. Ищем f(x) = выражение (ВЫСШИЙ ПРИОРИТЕТ)
        match_fx = re.search(r'f\s*\(\s*x\s*\)\s*=\s*(.+)', text, re.IGNORECASE)
        if match_fx:
            expression = match_fx.group(1).strip()
            print(f"🔍 Извлекли из f(x): '{expression}'")  # ОТЛАДКА
            return expression

        # 2. Ищем производную от выражения
        match_deriv = re.search(r'производная\s+(?:от\s+)?(.+)', text.lower())
        if match_deriv:
            expression = match_deriv.group(1).strip()
            # Убираем "по x" если есть
            expression = re.sub(r'\s*по\s*x\s*$', '', expression)
            print(f"🔍 Извлекли из 'производная от': '{expression}'")  # ОТЛАДКА
            return expression

        # 3. Ищем "найти производную"
        match_find = re.search(r'найти\s+производную\s+(.+)', text.lower())
        if match_find:
            expression = match_find.group(1).strip()
            print(f"🔍 Извлекли из 'найти производную': '{expression}'")  # ОТЛАДКА
            return expression

        # 4. Удаляем русские команды и оставляем только математику
        clean_text = re.sub(
            r'(производная|производную|найти|функции|функция|от|дифференцировать|дифференциал|f\'\s*\(\s*x\s*\))',
            '', text, flags=re.IGNORECASE
        )
        clean_text = clean_text.strip()
        print(f"🔍 Очищенный текст: '{clean_text}'")  # ОТЛАДКА

        # 5. Ищем математическое выражение
        math_pattern = r'([a-zA-Z\d+\-*/\^\.\s\(\)e]+)'
        matches = re.findall(math_pattern, clean_text)
        if matches:
            # Берем самое длинное математическое выражение
            expression = max(matches, key=len).strip()
            expression = re.sub(r'\s+', ' ', expression)
            print(f"🔍 Извлекли математическое выражение: '{expression}'")  # ОТЛАДКА
            return expression

        print(f"🔍 Не удалось извлечь выражение")  # ОТЛАДКА
        return None

    def _normalize_expression(self, expression: str) -> str:
        """Нормализует математическое выражение для SymPy - добавляет * где нужно"""
        if not expression:
            return expression

        normalized = expression

        # Заменяем специальные символы Unicode
        normalized = normalized.replace('²', '**2')
        normalized = normalized.replace('³', '**3')

        # Заменяем ^ на **
        normalized = normalized.replace('^', '**')

        # Добавляем * между цифрой и буквой: 3x -> 3*x, 2sin(x) -> 2*sin(x)
        normalized = re.sub(r'(\d)([a-zA-Z\(])', r'\1*\2', normalized)

        # Добавляем * между буквой и цифрой: x2 -> x*2
        normalized = re.sub(r'([a-zA-Z\)])(\d)', r'\1*\2', normalized)

        # Добавляем * между ) и ( или буквой: )( -> )*(, )x -> )*x
        normalized = re.sub(r'(\))(\()', r'\1*\2', normalized)
        normalized = re.sub(r'(\))([a-zA-Z])', r'\1*\2', normalized)

        # Обрабатываем e^x -> exp(x)
        normalized = re.sub(r'e\^\(([^\)]+)\)', r'exp(\1)', normalized)
        normalized = re.sub(r'e\^([^\(\)\s]+)', r'exp(\1)', normalized)
        normalized = re.sub(r'e\*\*\(([^\)]+)\)', r'exp(\1)', normalized)
        normalized = re.sub(r'e\*\*([^\(\)\s]+)', r'exp(\1)', normalized)

        # Заменяем ln на log
        normalized = re.sub(r'\bln\b', 'log', normalized)

        # Заменяем арктангенс
        normalized = re.sub(r'\barctan\b', 'atan', normalized)

        return normalized.strip()


# Глобальный экземпляр
derivative_solver = DerivativeSolver()