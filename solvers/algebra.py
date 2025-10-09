"""
Решатель алгебраических задач
"""

import sympy as sp
import logging
import re
from typing import Dict, Any
from sympy import symbols, parse_expr, simplify, expand, factor

logger = logging.getLogger(__name__)


class AlgebraSolver:
    """Решатель алгебраических задач"""

    def solve(self, text: str) -> Dict[str, Any]:
        """Решение алгебраических задач"""
        try:
            # Убираем слова команд перед парсингом
            clean_text = re.sub(r'упростить\s*', '', text, flags=re.IGNORECASE)
            clean_text = re.sub(r'разложить\s*', '', clean_text, flags=re.IGNORECASE)
            clean_text = re.sub(r'решить\s*', '', clean_text, flags=re.IGNORECASE)

            # Нормализуем математические выражения
            clean_text = clean_text.replace('^', '**')

            expr = parse_expr(clean_text)
            simplified = simplify(expr)
            expanded = expand(expr)
            factored = factor(expr)

            result = simplified
            operation = 'упрощение'

            if expanded != expr:
                result = expanded
                operation = 'раскрытие скобок'
            elif factored != expr:
                result = factored
                operation = 'факторизация'

            steps = [
                f"Исходное выражение: {sp.latex(expr)}",
                f"Операция: {operation}",
                f"Результат: {sp.latex(result)}"
            ]

            return {
                'success': True,
                'solution': str(result),
                'steps': steps,
                'latex': sp.latex(result),
                'explanation': f"Выполнено {operation} алгебраического выражения"
            }

        except Exception as e:
            logger.error(f"Ошибка алгебраических вычислений: {e}")
            return {
                'success': False,
                'solution': '',
                'steps': [],
                'latex': '',
                'explanation': f'Ошибка вычисления: {e}'
            }


# Глобальный экземпляр
algebra_solver = AlgebraSolver()