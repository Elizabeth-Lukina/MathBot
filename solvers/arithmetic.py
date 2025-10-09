"""
Решатель арифметических задач
"""

import sympy as sp
import logging
import re
import math
from typing import Dict, Any

logger = logging.getLogger(__name__)

class ArithmeticSolver:
    """Решатель арифметических выражений"""

    def solve(self, text: str) -> Dict[str, Any]:
        """Решение арифметических задач"""
        try:
            # Нормализуем математические функции
            normalized_text = self._normalize_mathematical_text(text)
            logger.info(f"Нормализованный текст: {normalized_text}")

            # Очищаем для eval
            clean_text = self._clean_arithmetic_text(normalized_text)

            try:
                # Безопасный eval с математическими функциями
                safe_dict = {
                    'sqrt': math.sqrt,
                    'sin': math.sin,
                    'cos': math.cos,
                    'tan': math.tan,
                    'log': math.log,
                    'log10': math.log10,
                    'exp': math.exp,
                    'pi': math.pi,
                    'e': math.e
                }

                # Добавляем базовые математические операции
                safe_dict.update({
                    '__builtins__': {},
                    'abs': abs,
                    'round': round,
                    'min': min,
                    'max': max,
                    'sum': sum
                })

                result = eval(clean_text, {"__builtins__": None}, safe_dict)
                steps = [f"Вычисление: {text} = {result}"]

                return {
                    'success': True,
                    'solution': str(result),
                    'steps': steps,
                    'latex': str(result),
                    'explanation': "Выполнены арифметические вычисления"
                }
            except Exception as eval_error:
                logger.warning(f"Eval не сработал: {eval_error}, пробуем SymPy")
                # Пробуем через SymPy
                return self._solve_with_sympy(normalized_text)

        except Exception as e:
            logger.error(f"Ошибка арифметических вычислений: {e}")
            return {
                'success': False,
                'solution': text,
                'steps': [],
                'latex': text,
                'explanation': f'Ошибка вычисления: {e}'
            }

    def _solve_with_sympy(self, text: str) -> Dict[str, Any]:
        """Решение через SymPy"""
        try:
            from sympy import parse_expr, N

            expr = parse_expr(text)
            result = N(expr)  # Численное вычисление

            steps = [
                f"Выражение: {text}",
                f"Вычисление через SymPy: {result}"
            ]

            return {
                'success': True,
                'solution': str(result),
                'steps': steps,
                'latex': str(result),
                'explanation': "Выполнены вычисления с помощью SymPy"
            }
        except Exception as e:
            logger.error(f"Ошибка SymPy вычислений: {e}")
            return {
                'success': False,
                'solution': text,
                'steps': ["Не удалось вычислить выражение"],
                'latex': text,
                'explanation': "Выражение требует ручного решения"
            }

    def _normalize_mathematical_text(self, text: str) -> str:
        """Нормализация математического текста"""
        replacements = {
            'син': 'sin', 'кос': 'cos', 'тан': 'tan',
            'корень': 'sqrt', 'пи': 'pi', 'е': 'e'
        }

        text_normalized = text
        for russian, english in replacements.items():
            text_normalized = re.sub(russian, english, text_normalized, flags=re.IGNORECASE)

        text_normalized = text_normalized.replace('π', 'pi')
        text_normalized = text_normalized.replace('^', '**')
        return text_normalized.strip()

    def _clean_arithmetic_text(self, text: str) -> str:
        """Очистка арифметического текста"""
        # Убираем лишние пробелы
        text = ' '.join(text.split())
        # Заменяем запятые на точки для десятичных чисел
        text = re.sub(r'(\d),(\d)', r'\1.\2', text)
        return text.strip()

# Глобальный экземпляр
arithmetic_solver = ArithmeticSolver()