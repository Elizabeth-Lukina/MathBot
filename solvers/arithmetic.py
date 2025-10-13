"""
Решатель арифметических задач
"""

import sympy as sp
import logging
import re
import math
from typing import Dict, Any
from sympy import parse_expr, N

logger = logging.getLogger(__name__)

class ArithmeticSolver:
    """Решатель арифметических выражений"""

    def solve(self, text: str) -> Dict[str, Any]:
        """Решение арифметических задач"""
        try:
            # Импортируем нормализатор
            from .expression_normalizer import expression_normalizer
            
            # Нормализуем математические функции
            normalized_text = expression_normalizer.normalize_mathematical_text(text)
            logger.info(f"Нормализованный текст: {normalized_text}")

            # Очищаем для eval
            clean_text = expression_normalizer.clean_arithmetic_text(normalized_text)

            # Сначала пробуем безопасный eval
            result, steps, explanation = self._try_safe_eval(clean_text)
            if result is not None:
                return {
                    'success': True,
                    'solution': str(result),
                    'steps': steps,
                    'latex': str(result),
                    'explanation': explanation
                }

            # Если eval не сработал, пробуем SymPy
            return self._solve_with_sympy(clean_text, text)

        except Exception as e:
            logger.error(f"Ошибка арифметических вычислений: {e}")
            return {
                'success': False,
                'solution': text,
                'steps': [],
                'latex': text,
                'explanation': f'Ошибка вычисления: {e}'
            }

    def _try_safe_eval(self, text: str):
        """Пробует безопасный eval вычислений"""
        try:
            # Безопасный eval с математическими функциями
            safe_dict = {
                # Математические функции
                'sqrt': math.sqrt,
                'sin': math.sin,
                'cos': math.cos,
                'tan': math.tan,
                'log': math.log,
                'log10': math.log10,
                'exp': math.exp,
                'pi': math.pi,
                'e': math.e,
                
                # Базовые математические операции
                '__builtins__': {},
                'abs': abs,
                'round': round,
                'min': min,
                'max': max,
                'sum': sum,
                
                # Дополнительные функции
                'radians': math.radians,
                'degrees': math.degrees,
                'factorial': math.factorial,
                'pow': math.pow
            }

            # Проверяем, что текст безопасен для eval
            if self._is_safe_for_eval(text):
                result = eval(text, {"__builtins__": None}, safe_dict)
                steps = [f"Вычисление: {text} = {result}"]
                explanation = "Выполнены арифметические вычисления"
                return result, steps, explanation
            else:
                return None, [], "Выражение содержит небезопасные операции"
                
        except Exception as eval_error:
            logger.warning(f"Eval не сработал: {eval_error}")
            return None, [], f"Eval вычисление не удалось: {eval_error}"

    def _is_safe_for_eval(self, text: str) -> bool:
        """Проверяет безопасность выражения для eval"""
        # Разрешенные символы и функции
        safe_pattern = r'^[\d\s\.\+\-\*/\()\sincostanlogexpsqrtpiabsroundminmaxsumradiansdegreesfactorialpow,]+$'
        
        # Проверяем на наличие опасных конструкций
        dangerous_patterns = [
            r'__',  # двойное подчеркивание
            r'import',
            r'open',
            r'exec',
            r'eval',
            r'compile',
            r'file',
            r'os\.',
            r'sys\.',
            r'subprocess'
        ]
        
        # Проверяем безопасность
        if not re.match(safe_pattern, text.replace(' ', '')):
            return False
            
        for pattern in dangerous_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return False
                
        return True

    def _solve_with_sympy(self, clean_text: str, original_text: str) -> Dict[str, Any]:
        """Решение через SymPy"""
        try:
            # Дополнительная нормализация для SymPy
            sympy_text = self._prepare_for_sympy(clean_text)
            
            expr = parse_expr(sympy_text)
            result = N(expr)  # Численное вычисление

            steps = [
                f"Исходное выражение: {original_text}",
                f"Нормализованное: {clean_text}",
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
            return self._solve_complex_expression(clean_text, original_text)

    def _prepare_for_sympy(self, text: str) -> str:
        """Подготавливает выражение для SymPy"""
        # Добавляем операторы умножения где нужно
        normalized = re.sub(r'(\d)([a-zA-Z\(])', r'\1*\2', text)  # 2x -> 2*x
        normalized = re.sub(r'([a-zA-Z\)])(\d)', r'\1*\2', normalized)  # x2 -> x*2
        normalized = re.sub(r'(\))(\()', r'\1*\2', normalized)  # )( -> )*(
        
        return normalized

    def _solve_complex_expression(self, clean_text: str, original_text: str) -> Dict[str, Any]:
        """Решение сложных выражений с пошаговым вычислением"""
        try:
            # Разбиваем выражение на части и вычисляем пошагово
            steps = [f"Исходное выражение: {original_text}"]
            
            # Пробуем вычислить части выражения
            result = self._compute_step_by_step(clean_text, steps)
            
            if result is not None:
                steps.append(f"Финальный результат: {result}")
                return {
                    'success': True,
                    'solution': str(result),
                    'steps': steps,
                    'latex': str(result),
                    'explanation': "Выражение вычислено пошагово"
                }
            else:
                return {
                    'success': False,
                    'solution': original_text,
                    'steps': ["Не удалось вычислить выражение"],
                    'latex': original_text,
                    'explanation': "Выражение требует ручного решения или содержит неподдерживаемые операции"
                }
                
        except Exception as e:
            logger.error(f"Ошибка пошагового вычисления: {e}")
            return {
                'success': False,
                'solution': original_text,
                'steps': [f"Ошибка вычисления: {e}"],
                'latex': original_text,
                'explanation': f"Не удалось вычислить выражение: {e}"
            }

    def _compute_step_by_step(self, expression: str, steps: list):
        """Вычисляет выражение пошагово"""
        try:
            # Простые арифметические операции
            if re.match(r'^[\d\s\.\+\-\*/\()]+$', expression.replace(' ', '')):
                # Безопасное вычисление базовых арифметических операций
                result = eval(expression, {"__builtins__": None}, {})
                steps.append(f"Арифметическое вычисление: {expression} = {result}")
                return result
                
            # Выражения с математическими функциями
            elif any(func in expression for func in ['sin', 'cos', 'tan', 'log', 'exp', 'sqrt']):
                # Используем SymPy для сложных выражений
                expr = parse_expr(expression)
                result = N(expr)
                steps.append(f"Вычисление с функциями: {expression} = {result}")
                return result
                
            return None
            
        except Exception as e:
            logger.warning(f"Пошаговое вычисление не удалось: {e}")
            return None

# Глобальный экземпляр
arithmetic_solver = ArithmeticSolver()
