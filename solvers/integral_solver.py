import sympy as sp
import logging
import re
from sympy import symbols, integrate, simplify

logger = logging.getLogger(__name__)


class IntegralSolver:
    def __init__(self):
        self.x = symbols('x')
        logger.info("IntegralSolver инициализирован")

    def solve_with_steps(self, text):
        """Решение интегралов"""
        steps = []

        try:
            steps.append({
                'description': 'Исходный интеграл',
                'formula': text
            })

            # Извлекаем подынтегральное выражение
            integral_text = self.extract_integral_expression(text)

            # Предварительная обработка
            integral_text = self.preprocess_text(integral_text)

            steps.append({
                'description': 'Очищенное выражение',
                'formula': f'∫{integral_text} dx'
            })

            try:
                expr = sp.sympify(integral_text)
            except Exception as e:
                return {'success': False, 'error': f'Ошибка парсинга выражения: {e}'}

            steps.append({
                'description': 'Подынтегральная функция',
                'formula': f'f(x) = {sp.latex(expr)}'
            })

            # Интегрирование
            result = integrate(expr, self.x)

            steps.append({
                'description': 'Применение правил интегрирования',
                'formula': f'∫{sp.latex(expr)} dx = {sp.latex(result)} + C'
            })

            # Определяем метод
            method = self.get_integration_method(expr)
            steps.append({
                'description': 'Метод интегрирования',
                'formula': method
            })

            return {
                'success': True,
                'solution': f'{result} + C',
                'steps': steps,
                'problem_type': 'integral',
                'processing_time': 0.2,
                'explanation': 'Интеграл решен методами интегрирования'
            }

        except Exception as e:
            logger.error(f"Ошибка решения интеграла: {e}")
            return {'success': False, 'error': f'Ошибка решения интеграла: {e}'}

    def extract_integral_expression(self, text):
        """Извлечение подынтегрального выражения"""
        # Убираем символы интеграла и дифференциала
        text_clean = re.sub(r'[∫]', '', text)
        text_clean = re.sub(r'd[x-y-z]', '', text_clean)
        text_clean = re.sub(r'(integral|интеграл)', '', text_clean, flags=re.IGNORECASE)

        # Убираем лишние пробелы
        text_clean = ' '.join(text_clean.split())
        return text_clean.strip()

    def preprocess_text(self, text):
        """Предварительная обработка текста"""
        text = text.replace('^', '**')
        text = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', text)
        text = re.sub(r'([a-zA-Z])(\d)', r'\1*\2', text)
        return text

    def get_integration_method(self, expr):
        """Определение метода интегрирования"""
        expr_str = str(expr)

        if 'sin' in expr_str or 'cos' in expr_str:
            return 'Тригонометрическое интегрирование'
        elif 'exp' in expr_str:
            return 'Интегрирование экспоненты'
        elif 'log' in expr_str:
            return 'Интегрирование по частям'
        else:
            return 'Непосредственное интегрирование'