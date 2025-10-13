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
    """Класс для решения различных типов уравнений"""

    def solve(self, text: str) -> Dict[str, Any]:
        """
        Основной метод для решения уравнений

        Args:
            text: Текст с уравнением для решения

        Returns:
            Словарь с результатом решения уравнения
        """
        try:
            if '=' not in text:
                return self._create_error_response('Уравнение должно содержать знак равенства')

            # Извлекаем и нормализуем уравнение
            equation_text = self._extract_equation(text)
            normalized_text = self._normalize_equation(equation_text)
            logger.info(f"Нормализованное уравнение: {normalized_text}")

            # Разделяем на левую и правую части
            left_side, right_side = self._split_equation(normalized_text)
            if not left_side or not right_side:
                return self._create_error_response('Не удалось разделить уравнение на левую и правую части')

            # Нормализуем каждую часть отдельно
            left_normalized = self._normalize_expression(left_side)
            right_normalized = self._normalize_expression(right_side)

            logger.info(f"Левая часть: '{left_normalized}', Правая часть: '{right_normalized}'")

            # Парсим выражения
            left_expr = self._parse_expression(left_normalized)
            right_expr = self._parse_expression(right_normalized)

            if left_expr is None or right_expr is None:
                return self._create_error_response('Ошибка парсинга выражения')

            # Создаем уравнение
            equation = sp.Eq(left_expr, right_expr)
            variables = equation.free_symbols

            if not variables:
                return {
                    'success': True,
                    'solution': 'Уравнение не содержит переменных',
                    'steps': [],
                    'latex': '',
                    'explanation': 'Уравнение не содержит переменных для решения'
                }

            # Выбираем лучший метод решения
            var = list(variables)[0]
            solutions = self._solve_with_best_method(equation, var)

            # Форматируем решение
            formatted_solution = self._format_solution(solutions, var)

            steps = [
                f"Уравнение: {sp.latex(equation)}",
                f"Переменная: {var}",
                f"Решение: {formatted_solution}"
            ]

            latex_solution = self._format_latex_solution(solutions, var)

            return {
                'success': True,
                'solution': formatted_solution,
                'steps': steps,
                'latex': latex_solution,
                'explanation': f"Решено уравнение с переменной {var}"
            }

        except Exception as e:
            logger.error(f"Ошибка решения уравнения: {e}")
            return self._create_error_response(f'Ошибка решения: {e}')

    def _extract_equation(self, text: str) -> str:
        """
        Извлекает уравнение из текста

        Args:
            text: Исходный текст с уравнением

        Returns:
            Очищенное уравнение
        """
        # Убираем русские команды
        clean_text = self._remove_equation_commands(text)

        # Ищем математическое выражение с равенством
        equation_patterns = [
            r'([^=]+=[^=]+)',  # основное уравнение
            r'решить\s*(.+)',  # после команды "решить"
            r'найти\s*(.+)',  # после команды "найти"
        ]

        for pattern in equation_patterns:
            match = re.search(pattern, clean_text, re.IGNORECASE)
            if match:
                equation = match.group(1).strip()
                if '=' in equation:
                    return equation

        # Если не нашли паттерн, возвращаем очищенный текст
        return clean_text

    def _remove_equation_commands(self, text: str) -> str:
        """Удаляет команды связанные с уравнениями из текста"""
        equation_commands = [
            'решить', 'уравнение', 'найти', 'вычислить', 'пример',
            'корень', 'корни', 'решение'
        ]

        clean_text = text
        for command in equation_commands:
            clean_text = re.sub(command, '', clean_text, flags=re.IGNORECASE)

        return clean_text.strip()

    def _split_equation(self, equation: str):
        """
        Разделяет уравнение на левую и правую части

        Args:
            equation: Уравнение в виде строки

        Returns:
            Кортеж (левая_часть, правая_часть)
        """
        if '=' not in equation:
            return None, None

        parts = equation.split('=', 1)
        if len(parts) != 2:
            return None, None

        left_side = parts[0].strip()
        right_side = parts[1].strip()

        return left_side, right_side

    def _normalize_equation(self, text: str) -> str:
        """Нормализует уравнение для обработки"""
        # Импортируем общий нормализатор
        from .expression_normalizer import expression_normalizer

        # Используем нормализацию уравнений
        normalized = expression_normalizer.normalize_equation(text)

        return normalized

    def _normalize_expression(self, expression: str) -> str:
        """Нормализует математическое выражение"""
        # Импортируем общий нормализатор
        from .expression_normalizer import expression_normalizer

        # Используем общую нормализацию выражений
        normalized = expression_normalizer.normalize_expression(expression)

        return normalized

    def _parse_expression(self, expression: str):
        """Парсит математическое выражение с обработкой ошибок"""
        try:
            return parse_expr(expression)
        except Exception as e:
            logger.error(f"Ошибка парсинга выражения '{expression}': {e}")
            return None

    def _solve_with_best_method(self, equation, var):
        """
        Выбирает лучший метод решения уравнения

        Args:
            equation: Уравнение SymPy
            var: Переменная для решения

        Returns:
            Решение уравнения
        """
        try:
            # Для линейных и полиномиальных уравнений используем solve
            solutions = solve(equation, var, dict=True)
            if solutions:
                # Извлекаем значения из словарей
                return [sol[var] for sol in solutions]

            # Для тригонометрических уравнений используем solveset
            if any(func in str(equation) for func in ['sin', 'cos', 'tan', 'cot']):
                solution_set = solveset(equation, var)
                if solution_set != S.EmptySet:
                    return solution_set

            # Для уравнений с модулем
            if any(func in str(equation) for func in ['Abs', 'abs']):
                return self._solve_abs_equation(equation, var)

            # Для трансцендентных уравнений пробуем численное решение
            try:
                # Ищем численное решение вблизи 0
                numerical_sol = nsolve(equation, var, 0)
                return [numerical_sol]
            except:
                pass

            # Пробуем общий метод solveset
            solution_set = solveset(equation, var)
            if solution_set != S.EmptySet:
                return solution_set

            return "Не удалось найти решение"

        except Exception as e:
            logger.warning(f"Метод решения не сработал: {e}")
            return "Требуется специальный метод решения"

    def _solve_abs_equation(self, equation, var):
        """Решает уравнения с модулем"""
        try:
            # Уравнение вида Abs(expr) = value
            abs_exprs = list(equation.find(sp.Abs))
            if not abs_exprs:
                return "Не является уравнением с модулем"

            abs_expr = abs_exprs[0]
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

    def _format_solution(self, solutions, var):
        """Форматирует решение для вывода"""
        if isinstance(solutions, str):
            return solutions

        if hasattr(solutions, '__iter__') and not isinstance(solutions, sp.Set):
            if len(solutions) == 0:
                return "Нет решений"
            elif len(solutions) == 1:
                return f"{var} = {solutions[0]}"
            else:
                solutions_str = ", ".join([f"{var} = {sol}" for sol in solutions])
                return f"Решения: {solutions_str}"
        else:
            # Для объектов Set
            if solutions == S.EmptySet:
                return "Нет решений"
            else:
                return f"{var} ∈ {solutions}"

    def _format_latex_solution(self, solutions, var):
        """Форматирует решение в LaTeX"""
        if isinstance(solutions, str):
            return solutions

        if hasattr(solutions, '__iter__') and not isinstance(solutions, sp.Set):
            if len(solutions) == 0:
                return "\\text{Нет решений}"
            elif len(solutions) == 1:
                return f"{sp.latex(var)} = {sp.latex(solutions[0])}"
            else:
                solutions_latex = ", ".join([f"{sp.latex(var)} = {sp.latex(sol)}" for sol in solutions])
                return f"\\text{{Решения: }} {solutions_latex}"
        else:
            # Для объектов Set
            if solutions == S.EmptySet:
                return "\\text{Нет решений}"
            else:
                return f"{sp.latex(var)} \\in {sp.latex(solutions)}"

    def _create_error_response(self, message: str) -> Dict[str, Any]:
        """Создает стандартизированный ответ с ошибкой"""
        return {
            'success': False,
            'solution': '',
            'steps': [],
            'latex': '',
            'explanation': message
        }


# Глобальный экземпляр решателя
equation_solver = EquationSolver()
