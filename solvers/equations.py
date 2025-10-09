"""
Решатель уравнений
"""

import sympy as sp
import logging
import re
from typing import Dict, Any
from sympy import symbols, solve, parse_expr, nsolve, solveset, S, Abs
from sympy.solvers.solveset import solveset
from sympy.calculus.util import continuous_domain

logger = logging.getLogger(__name__)


class EquationSolver:
    """Решатель уравнений"""

    def solve(self, text: str) -> Dict[str, Any]:
        """Решение уравнений"""
        try:
            if '=' not in text:
                return {'success': False, 'solution': '', 'steps': [], 'latex': '',
                        'explanation': 'Нет знака равенства'}

            # Нормализуем всё уравнение перед обработкой
            normalized_text = self._normalize_equation(text)
            logger.info(f"Нормализованное уравнение: {normalized_text}")

            # Разделяем на левую и правую части
            left_side, right_side = normalized_text.split('=', 1)

            # Нормализуем каждую часть отдельно
            left_normalized = self._normalize_expression(left_side.strip())
            right_normalized = self._normalize_expression(right_side.strip())

            logger.info(f"Левая часть: '{left_normalized}', Правая часть: '{right_normalized}'")

            left_expr = parse_expr(left_normalized)
            right_expr = parse_expr(right_normalized)

            equation = sp.Eq(left_expr, right_expr)
            variables = equation.free_symbols

            if not variables:
                return {
                    'success': True,
                    'solution': 'Нет переменных для решения',
                    'steps': [],
                    'latex': '',
                    'explanation': ''
                }

            # Пробуем разные методы решения
            var = list(variables)[0]
            solutions = self._solve_with_best_method(equation, var)

            steps = [
                f"Уравнение: {sp.latex(equation)}",
                f"Переменная: {var}",
                f"Решение: {solutions}"
            ]

            latex_solution = sp.latex(solutions) if solutions else "Нет решений"

            return {
                'success': True,
                'solution': str(solutions),
                'steps': steps,
                'latex': latex_solution,
                'explanation': f"Решено уравнение с переменной {var}"
            }

        except Exception as e:
            logger.error(f"Ошибка решения уравнения: {e}")
            return {
                'success': False,
                'solution': '',
                'steps': [],
                'latex': '',
                'explanation': f'Ошибка решения: {e}'
            }

    def _solve_with_best_method(self, equation, var):
        """Выбирает лучший метод решения уравнения"""
        try:
            # Для тригонометрических уравнений используем solveset
            if any(func in str(equation) for func in ['sin', 'cos', 'tan']):
                solution_set = solveset(equation, var)
                if solution_set != S.EmptySet:
                    return solution_set

            # Для уравнений с модулем
            if 'Abs' in str(equation):
                return self._solve_abs_equation(equation, var)

            # Пробуем аналитическое решение
            solutions = solve(equation, var, dict=True)
            if solutions:
                # Извлекаем значения из словарей
                return [sol[var] for sol in solutions]

            # Для трансцендентных уравнений пробуем численное решение
            try:
                # Ищем численное решение вблизи 0
                numerical_sol = nsolve(equation, var, 0)
                return [numerical_sol]
            except:
                pass

            return "Не удалось найти решение"

        except Exception as e:
            logger.warning(f"Метод решения не сработал: {e}")
            return "Требуется специальный метод решения"

    def _solve_abs_equation(self, equation, var):
        """Решает уравнения с модулем"""
        try:
            # Уравнение вида Abs(expr) = value
            abs_expr = list(equation.find(sp.Abs))[0]
            inside_abs = abs_expr.args[0]

            # Создаем два уравнения: expr = value и expr = -value
            eq1 = sp.Eq(inside_abs, equation.rhs)
            eq2 = sp.Eq(inside_abs, -equation.rhs)

            solutions1 = solve(eq1, var)
            solutions2 = solve(eq2, var)

            # Объединяем решения
            all_solutions = solutions1 + solutions2
            return all_solutions if all_solutions else "Нет решений"

        except Exception as e:
            logger.warning(f"Ошибка решения уравнения с модулем: {e}")
            return "Не удалось решить уравнение с модулем"

    def _normalize_equation(self, text: str) -> str:
        """Нормализует всё уравнение"""
        # Удаляем русские слова
        clean_text = self._remove_russian_words(text)

        # Заменяем ^ на **
        normalized = clean_text.replace('^', '**')

        return normalized

    def _normalize_expression(self, expression: str) -> str:
        """Нормализует математическое выражение для SymPy"""
        # Добавляем * между цифрой и буквой: 2x -> 2*x, 3sin(x) -> 3*sin(x)
        normalized = re.sub(r'(\d)([a-zA-Z\(])', r'\1*\2', expression)

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

        return normalized.strip()

    def _remove_russian_words(self, text: str) -> str:
        """Удаляет русские слова из текста"""
        russian_words = ['решить', 'уравнение', 'найти', 'вычислить', 'пример']
        clean_text = text
        for word in russian_words:
            clean_text = re.sub(word, '', clean_text, flags=re.IGNORECASE)
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        return clean_text


# Глобальный экземпляр
equation_solver = EquationSolver()