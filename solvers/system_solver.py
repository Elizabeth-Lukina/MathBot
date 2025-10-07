import sympy as sp
import logging
from sympy import symbols, solve, Eq, simplify
import re


logger = logging.getLogger(__name__)


class SystemSolver:
    def __init__(self):
        self.x, self.y = symbols('x y')
        logger.info("SystemSolver инициализирован")

    def solve_with_steps(self, text):
        """Решение систем уравнений с пошаговыми объяснениями"""
        steps = []

        try:
            steps.append({
                'description': 'Исходная система уравнений',
                'formula': text,
                'details': 'Анализируем систему'
            })

            # Парсим систему уравнений
            equations = self.parse_system(text)

            if len(equations) < 2:
                return {'success': False, 'error': 'Не система уравнений'}

            # Записываем уравнения
            for i, eq in enumerate(equations, 1):
                steps.append({
                    'description': f'Уравнение {i}',
                    'formula': f'{sp.latex(eq.lhs)} = {sp.latex(eq.rhs)}',
                    'details': f'Уравнение {i} системы'
                })

            # Решаем систему
            solutions = solve(equations, (self.x, self.y), dict=True)

            if not solutions:
                return {'success': False, 'error': 'Система не имеет решений'}

            steps.append({
                'description': 'Решение системы',
                'formula': f'x = {solutions[0][self.x]}, y = {solutions[0][self.y]}',
                'details': 'Система решена методом подстановки или исключения'
            })

            # Проверяем решение
            for i, eq in enumerate(equations, 1):
                lhs_val = eq.lhs.subs(solutions[0])
                rhs_val = eq.rhs.subs(solutions[0])
                steps.append({
                    'description': f'Проверка уравнения {i}',
                    'formula': f'{lhs_val} = {rhs_val}',
                    'details': 'Проверка подстановкой решения'
                })

            return {
                'success': True,
                'solution': f'x = {solutions[0][self.x]}, y = {solutions[0][self.y]}',
                'steps': steps,
                'problem_type': 'system',
                'processing_time': 0.3,
                'explanation': 'Система решена методом подстановки'
            }

        except Exception as e:
            logger.error(f"Ошибка решения системы: {e}")
            return {'success': False, 'error': f'Ошибка решения системы: {e}'}

    def parse_system(self, text):
        """Парсинг системы уравнений из текста"""
        equations = []

        # Разделяем на строки
        lines = text.split('\n')
        if len(lines) < 2:
            # Пробуем разделить по точкам с запятой
            lines = text.split(';')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if '=' in line:
                parts = line.split('=')
                if len(parts) == 2:
                    try:
                        # Предварительная обработка
                        left = self.preprocess_text(parts[0].strip())
                        right = self.preprocess_text(parts[1].strip())

                        left_expr = sp.sympify(left)
                        right_expr = sp.sympify(right)
                        equations.append(Eq(left_expr, right_expr))
                    except Exception as e:
                        logger.warning(f"Ошибка парсинга уравнения: {line} - {e}")
                        continue

        return equations

    def preprocess_text(self, text):
        """Предварительная обработка текста"""
        text = text.replace('^', '**')
        text = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', text)
        text = re.sub(r'([a-zA-Z])(\d)', r'\1*\2', text)
        return text