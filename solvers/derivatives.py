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

            # Нормализуем выражение - добавляем * где нужно
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

            steps = [
                f"Исходная функция: {sp.latex(expr)}",
                f"Переменная дифференцирования: {var}",
                f"Производная: {sp.latex(derivative)}"
            ]

            return {
                'success': True,
                'solution': str(derivative),
                'steps': steps,
                'latex': sp.latex(derivative),
                'explanation': f"Найдена производная по переменной {var}"
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
        # Удаляем русские команды
        clean_text = re.sub(
            r'(производная|производную|найти|функции|функция|от|дифференцировать|дифференциал|f\'\s*\(\s*x\s*\))',
            '', text, flags=re.IGNORECASE
        )
        clean_text = clean_text.strip()

        # Ищем f(x) = выражение
        match_fx = re.search(r'f\s*\(\s*x\s*\)\s*=\s*(.+)', text, re.IGNORECASE)
        if match_fx:
            return match_fx.group(1).strip()

        # Ищем математическое выражение (включая e^x, sin(x) и т.д.)
        math_pattern = r'([a-zA-Z\d+\-*/\^\.\s\(\)e]+)'
        matches = re.findall(math_pattern, clean_text)
        if matches:
            # Берем самое длинное математическое выражение
            return max(matches, key=len).strip()

        return clean_text

    def _normalize_expression(self, expression: str) -> str:
        """Нормализует математическое выражение для SymPy - добавляет * где нужно"""
        # Сначала заменяем ^ на **
        normalized = expression.replace('^', '**')

        # Добавляем * между цифрой и буквой: 3x -> 3*x, 2sin(x) -> 2*sin(x)
        normalized = re.sub(r'(\d)([a-zA-Z\(])', r'\1*\2', normalized)

        # Добавляем * между буквой и цифрой: x2 -> x*2
        normalized = re.sub(r'([a-zA-Z\)])(\d)', r'\1*\2', normalized)

        # Добавляем * между ) и ( или буквой: )( -> )*(, )x -> )*x
        normalized = re.sub(r'(\))(\()', r'\1*\2', normalized)
        normalized = re.sub(r'(\))([a-zA-Z])', r'\1*\2', normalized)

        # Обрабатываем e^x -> exp(x) - УЛУЧШЕННАЯ РЕГУЛЯРКА
        # Сначала обрабатываем e^(сложное выражение)
        normalized = re.sub(r'e\^\(([^\)]+)\)', r'exp(\1)', normalized)
        # Затем e^простое_выражение (без скобок)
        normalized = re.sub(r'e\^([^\(\)\s]+)', r'exp(\1)', normalized)

        # Также обрабатываем e**x -> exp(x)
        normalized = re.sub(r'e\*\*\(([^\)]+)\)', r'exp(\1)', normalized)
        normalized = re.sub(r'e\*\*([^\(\)\s]+)', r'exp(\1)', normalized)

        # Заменяем ln на log (SymPy использует log для натурального логарифма)
        normalized = re.sub(r'\bln\b', 'log', normalized)

        # Заменяем arctan на atan
        normalized = re.sub(r'\barctan\b', 'atan', normalized)

        return normalized.strip()


# Глобальный экземпляр
derivative_solver = DerivativeSolver()