import sympy as sp
import logging
import re
from sympy import symbols, solve, Eq, simplify

logger = logging.getLogger(__name__)


class EquationSolver:
    def __init__(self):
        self.x = symbols('x')
        logger.info("EquationSolver инициализирован")

    def solve_with_steps(self, text):
        """Решение обычных уравнений"""
        steps = []

        try:
            if '=' not in text:
                return {'success': False, 'error': 'Отсутствует знак равенства'}

            # Предварительная обработка текста
            cleaned_text = self.preprocess_text(text)

            parts = cleaned_text.split('=')
            if len(parts) != 2:
                return {'success': False, 'error': 'Некорректный формат уравнения'}

            left, right = parts[0].strip(), parts[1].strip()

            steps.append({
                'description': 'Исходное уравнение',
                'formula': f'{left} = {right}'
            })

            # Парсим выражения
            try:
                left_expr = sp.sympify(left)
                right_expr = sp.sympify(right)
            except Exception as e:
                return {'success': False, 'error': f'Ошибка парсинга выражения: {e}'}

            equation = Eq(left_expr, right_expr)

            steps.append({
                'description': 'Парсинг уравнения',
                'formula': f'{sp.latex(left_expr)} = {sp.latex(right_expr)}'
            })

            # Приведение к стандартному виду
            equation_std = Eq(left_expr - right_expr, 0)
            steps.append({
                'description': 'Перенос всех слагаемых в левую часть',
                'formula': f'{sp.latex(equation_std.lhs)} = 0'
            })

            # Упрощение
            simplified = simplify(equation_std.lhs)
            if simplified != equation_std.lhs:
                steps.append({
                    'description': 'Упрощение выражения',
                    'formula': f'{sp.latex(simplified)} = 0'
                })

            # Решение
            solutions = solve(equation, self.x, dict=True)

            if not solutions:
                return {'success': False, 'error': 'Уравнение не имеет решений'}

            solution_str = self.format_solutions(solutions)

            steps.append({
                'description': 'Решение уравнения',
                'formula': f'x = {solution_str}'
            })

            return {
                'success': True,
                'solution': solution_str,
                'steps': steps,
                'problem_type': 'equation',
                'processing_time': 0.1,
                'explanation': 'Уравнение решено алгебраическими методами'
            }

        except Exception as e:
            logger.error(f"Ошибка решения уравнения: {e}")
            return {'success': False, 'error': f'Ошибка решения уравнения: {e}'}

    def preprocess_text(self, text):
        """Предварительная обработка текста"""
        # Заменяем ^ на **
        text = text.replace('^', '**')
        # Добавляем * между цифрами и переменными
        text = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', text)
        text = re.sub(r'([a-zA-Z])(\d)', r'\1*\2', text)
        return text

    def format_solutions(self, solutions):
        """Форматирование решений"""
        sol_strs = []
        for sol in solutions:
            if self.x in sol:
                value = sol[self.x]
                if value.is_real:
                    sol_strs.append(f"{float(value):.6f}")
                else:
                    sol_strs.append(str(value))
        return ", ".join(sol_strs) if sol_strs else "∅"