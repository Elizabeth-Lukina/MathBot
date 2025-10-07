# -*- coding: utf-8 -*-
"""
Модуль для решения математических задач
Использует SymPy для символьных вычислений
"""

import sympy as sp
import logging
import re
import time
from sympy import symbols, solve, integrate, diff, simplify, expand, factor, Eq
from sympy import sin, cos, tan, cot, sec, csc, asin, acos, atan
from sympy import exp, log, sqrt, pi, oo, I

logger = logging.getLogger(__name__)


class MathSolver:
    """Класс для решения математических задач с помощью SymPy"""

    def __init__(self):
        # Общие переменные для вычислений
        self.x, self.y, self.z = symbols('x y z')
        self.a, self.b, self.c = symbols('a b c')
        logger.info("MathSolver инициализирован")

    def solve_with_steps(self, problem_text: str) -> dict:
        """
        Основная функция решения математической задачи

        Args:
            problem_text: Текст задачи

        Returns:
            Словарь с результатом решения
        """
        start_time = time.time()

        try:
            # Определяем тип задачи
            problem_type = self._detect_problem_type(problem_text)
            logger.info(f"Определен тип задачи: {problem_type}")

            # Очищаем и нормализуем текст
            cleaned_text = self._clean_text(problem_text)

            # Решаем в зависимости от типа
            if problem_type == "equation":
                result = self._solve_equation(cleaned_text)
            elif problem_type == "integral":
                result = self._solve_integral(cleaned_text)
            elif problem_type == "derivative":
                result = self._solve_derivative(cleaned_text)
            elif problem_type == "trigonometric":
                result = self._solve_trigonometric(cleaned_text)
            else:
                result = self._solve_expression(cleaned_text)

            processing_time = time.time() - start_time

            if result and result.get('success', False):
                return {
                    'success': True,
                    'problem_type': problem_type,
                    'solution': result['solution'],
                    'steps': result.get('steps', []),
                    'processing_time': processing_time,
                    'explanation': result.get('explanation', '')
                }
            else:
                return {
                    'success': False,
                    'processing_time': processing_time,
                    'error': result.get('error', 'Не удалось решить задачу')
                }

        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Ошибка решения задачи: {e}")
            return {
                'success': False,
                'processing_time': processing_time,
                'error': f'Ошибка: {str(e)}'
            }

    def _detect_problem_type(self, text: str) -> str:
        """Определение типа математической задачи"""
        text_lower = text.lower()

        if any(word in text_lower for word in ['∫', 'integral', 'интеграл']):
            return 'integral'
        elif any(word in text_lower for word in ['derivative', 'производная', 'd/d']):
            return 'derivative'
        elif any(word in text_lower for word in ['sin', 'cos', 'tan', 'cot', 'тригонометр']):
            return 'trigonometric'
        elif '=' in text_lower:
            return 'equation'
        else:
            return 'expression'

    def _clean_text(self, text: str) -> str:
        """Очистка математического текста"""
        if not text:
            return ""

        # Замены для математических символов
        replacements = {
            '^': '**', '×': '*', '÷': '/', '–': '-', '—': '-',
            'π': 'pi', '∞': 'oo', '√': 'sqrt',
            '²': '**2', '³': '**3', '⁻¹': '**-1',
            'sin': 'sin', 'cos': 'cos', 'tan': 'tan', 'tg': 'tan',
            'ctg': 'cot', 'sec': 'sec', 'csc': 'csc',
            'arcsin': 'asin', 'arccos': 'acos', 'arctan': 'atan',
            'ln': 'log', 'lg': 'log10', 'exp': 'exp'
        }

        cleaned = text
        for old, new in replacements.items():
            cleaned = cleaned.replace(old, new)

        # Убираем лишние пробелы
        cleaned = re.sub(r'\s*([+\-*/=()])\s*', r'\1', cleaned)

        # Добавляем * между числами и переменными
        cleaned = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', cleaned)
        cleaned = re.sub(r'([a-zA-Z])(\d)', r'\1*\2', cleaned)

        return cleaned.strip()

    def _solve_equation(self, text: str) -> dict:
        """Решение уравнений"""
        steps = []

        try:
            if '=' not in text:
                return {'success': False, 'error': 'Отсутствует знак равенства'}

            parts = text.split('=')
            if len(parts) != 2:
                return {'success': False, 'error': 'Неверный формат уравнения'}

            left, right = parts[0].strip(), parts[1].strip()

            # Парсим выражения
            left_expr = sp.sympify(left)
            right_expr = sp.sympify(right)
            equation = Eq(left_expr, right_expr)

            steps.append({
                'description': 'Исходное уравнение',
                'formula': f'{sp.latex(left_expr)} = {sp.latex(right_expr)}'
            })

            # Приведение к стандартному виду
            equation_std = Eq(left_expr - right_expr, 0)
            steps.append({
                'description': 'Приведение к стандартному виду',
                'formula': f'{sp.latex(equation_std.lhs)} = 0'
            })

            # Решение уравнения
            solutions = solve(equation, self.x, dict=True)

            if not solutions:
                return {'success': False, 'error': 'Уравнение не имеет решений'}

            solution_str = self._format_solutions(solutions)

            steps.append({
                'description': 'Решение уравнения',
                'formula': f'x = {solution_str}'
            })

            return {
                'success': True,
                'solution': solution_str,
                'steps': steps,
                'explanation': 'Уравнение решено алгебраическими методами'
            }

        except Exception as e:
            logger.error(f"Ошибка решения уравнения: {e}")
            return {'success': False, 'error': f'Ошибка решения уравнения: {e}'}

    def _solve_integral(self, text: str) -> dict:
        """Решение интегралов"""
        steps = []

        try:
            steps.append({
                'description': 'Исходный интеграл',
                'formula': text
            })

            # Извлекаем подынтегральное выражение
            integral_text = text.replace('∫', '').replace('integral', '').replace('интеграл', '').strip()
            integral_text = re.sub(r'd[x-y-z]$', '', integral_text).strip()

            # Парсим выражение
            expr = sp.sympify(integral_text)

            steps.append({
                'description': 'Подынтегральная функция',
                'formula': f'f(x) = {sp.latex(expr)}'
            })

            # Вычисляем интеграл
            result = integrate(expr, self.x)

            steps.append({
                'description': 'Применение правил интегрирования',
                'formula': f'∫{sp.latex(expr)} dx = {sp.latex(result)} + C'
            })

            return {
                'success': True,
                'solution': f'{result} + C',
                'steps': steps,
                'explanation': 'Интеграл решен методами интегрирования'
            }

        except Exception as e:
            logger.error(f"Ошибка решения интеграла: {e}")
            return {'success': False, 'error': f'Ошибка решения интеграла: {e}'}

    def _solve_derivative(self, text: str) -> dict:
        """Решение производных"""
        steps = []

        try:
            steps.append({
                'description': 'Исходное выражение',
                'formula': text
            })

            # Извлекаем функцию
            func_text = text.replace('производная', '').replace('derivative', '').replace('d/dx', '').strip()

            # Парсим выражение
            expr = sp.sympify(func_text)

            steps.append({
                'description': 'Функция для дифференцирования',
                'formula': f'f(x) = {sp.latex(expr)}'
            })

            # Вычисляем производную
            result = diff(expr, self.x)

            steps.append({
                'description': 'Применение правил дифференцирования',
                'formula': f"f'(x) = {sp.latex(result)}"
            })

            return {
                'success': True,
                'solution': str(result),
                'steps': steps,
                'explanation': 'Производная найдена правилами дифференцирования'
            }

        except Exception as e:
            logger.error(f"Ошибка решения производной: {e}")
            return {'success': False, 'error': f'Ошибка решения производной: {e}'}

    def _solve_trigonometric(self, text: str) -> dict:
        """Решение тригонометрических уравнений"""
        steps = []

        try:
            steps.append({
                'description': 'Исходное уравнение',
                'formula': text
            })

            if '=' not in text:
                return {'success': False, 'error': 'Не является уравнением'}

            parts = text.split('=')
            left, right = parts[0].strip(), parts[1].strip()

            # Парсим выражения
            left_expr = sp.sympify(left)
            right_expr = sp.sympify(right)
            equation = Eq(left_expr, right_expr)

            steps.append({
                'description': 'Приведение к стандартному виду',
                'formula': f'{sp.latex(left_expr)} = {sp.latex(right_expr)}'
            })

            # Решение уравнения
            solutions = solve(equation, self.x, dict=True)

            if not solutions:
                return {'success': False, 'error': 'Уравнение не имеет решений'}

            solution_str = self._format_solutions(solutions)

            steps.append({
                'description': 'Решение уравнения',
                'formula': f'x = {solution_str} + 2πn, n ∈ Z'
            })

            return {
                'success': True,
                'solution': solution_str,
                'steps': steps,
                'explanation': 'Тригонометрическое уравнение решено'
            }

        except Exception as e:
            logger.error(f"Ошибка решения тригонометрического уравнения: {e}")
            return {'success': False, 'error': f'Ошибка решения: {e}'}

    def _solve_expression(self, text: str) -> dict:
        """Упрощение выражений"""
        steps = []

        try:
            steps.append({
                'description': 'Исходное выражение',
                'formula': text
            })

            # Парсим выражение
            expr = sp.sympify(text)

            # Упрощаем
            result = simplify(expr)

            steps.append({
                'description': 'Упрощение выражения',
                'formula': f'Результат: {sp.latex(result)}'
            })

            return {
                'success': True,
                'solution': str(result),
                'steps': steps,
                'explanation': 'Выражение упрощено'
            }

        except Exception as e:
            logger.error(f"Ошибка упрощения выражения: {e}")
            return {'success': False, 'error': f'Ошибка упрощения: {e}'}

    def _format_solutions(self, solutions: list) -> str:
        """Форматирование решений"""
        if not solutions:
            return "∅"

        sol_strs = []
        for sol in solutions:
            if self.x in sol:
                value = sol[self.x]
                try:
                    if value.is_real:
                        sol_strs.append(f"{float(value):.6f}")
                    else:
                        sol_strs.append(str(value))
                except:
                    sol_strs.append(str(value))

        return ", ".join(sol_strs) if sol_strs else "∅"


# Глобальный экземпляр решателя
math_solver = MathSolver()