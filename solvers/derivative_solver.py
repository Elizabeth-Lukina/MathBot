import sympy as sp
import logging
import re
from sympy import symbols, diff, simplify, Derivative

logger = logging.getLogger(__name__)


class DerivativeSolver:
    def __init__(self):
        self.x = symbols('x')
        logger.info("DerivativeSolver инициализирован")

    def solve_with_steps(self, text):
        """Решение производных с пошаговыми объяснениями"""
        steps = []

        try:
            steps.append({
                'description': 'Исходное выражение для дифференцирования',
                'formula': text,
                'details': 'Анализируем функцию'
            })

            # Извлекаем функцию для дифференцирования
            derivative_text = self.extract_function(text)

            # Парсим выражение
            expr = sp.sympify(derivative_text)

            steps.append({
                'description': 'Функция для дифференцирования',
                'formula': f'f(x) = {sp.latex(expr)}',
                'details': 'Выражение преобразовано в математическую форму'
            })

            # Находим производную
            derivative = diff(expr, self.x)

            steps.append({
                'description': 'Применение правил дифференцирования',
                'formula': f"f'(x) = {sp.latex(derivative)}",
                'details': 'Использованы правила дифференцирования'
            })

            # Показываем примененные правила
            rules = self.identify_differentiation_rules(expr)
            for rule in rules:
                steps.append({
                    'description': 'Примененное правило',
                    'formula': rule,
                    'details': 'Правило дифференцирования'
                })

            # Упрощаем результат если нужно
            simplified = simplify(derivative)
            if simplified != derivative:
                steps.append({
                    'description': 'Упрощение результата',
                    'formula': f"f'(x) = {sp.latex(simplified)}",
                    'details': 'Производная упрощена'
                })
                derivative = simplified

            return {
                'success': True,
                'solution': str(derivative),
                'steps': steps,
                'explanation': 'Производная найдена с использованием правил дифференцирования'
            }

        except Exception as e:
            logger.error(f"Ошибка решения производной: {e}")
            return {'success': False, 'error': f'Ошибка решения производной: {e}'}

    def extract_function(self, text):
        """Извлечение функции из текста"""
        # Убираем ключевые слова
        text_clean = re.sub(r'(производная|derivative|d/d[x-y-z]|\'|\")', '', text, flags=re.IGNORECASE)
        text_clean = text_clean.replace('от', '').replace('of', '').strip()

        # Если осталось что-то вроде "f(x) = ...", берем правую часть
        if '=' in text_clean:
            parts = text_clean.split('=')
            if len(parts) == 2:
                return parts[1].strip()

        return text_clean.strip()

    def identify_differentiation_rules(self, expr):
        """Определение примененных правил дифференцирования"""
        rules = []
        expr_str = str(expr)

        # Проверяем различные правила
        if '**' in expr_str:
            rules.append('Степенное правило: d/dx[xⁿ] = n·xⁿ⁻¹')

        if 'sin' in expr_str or 'cos' in expr_str or 'tan' in expr_str:
            rules.append('Тригонометрические правила: d/dx[sin(x)] = cos(x), d/dx[cos(x)] = -sin(x)')

        if 'exp' in expr_str:
            rules.append('Экспоненциальное правило: d/dx[eˣ] = eˣ')

        if 'log' in expr_str:
            rules.append('Логарифмическое правило: d/dx[ln(x)] = 1/x')

        if '+' in expr_str or '-' in expr_str:
            rules.append('Правило суммы: d/dx[f(x) ± g(x)] = df(x) ± dg(x)')

        if '*' in expr_str and '**' not in expr_str:
            rules.append('Правило произведения: d/dx[f(x)·g(x)] = df(x)·g(x) + f(x)·dg(x)')

        if '/' in expr_str:
            rules.append('Правило частного: d/dx[f(x)/g(x)] = (df(x)·g(x) - f(x)·dg(x)) / g(x)²')

        if not rules:
            rules.append('Основное правило дифференцирования')

        return rules