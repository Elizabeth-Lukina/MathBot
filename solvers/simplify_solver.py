import sympy as sp
import logging
import re
from sympy import symbols, simplify, expand, factor, collect, together, apart, trigsimp

logger = logging.getLogger(__name__)


class SimplifySolver:
    def __init__(self):
        self.x = symbols('x')
        logger.info("SimplifySolver инициализирован")

    def solve_with_steps(self, text):
        """Упрощение выражений с пошаговыми объяснениями"""
        steps = []

        try:
            steps.append({
                'description': 'Исходное выражение',
                'formula': text,
                'details': 'Начинаем упрощение'
            })

            # Предварительная обработка
            cleaned_text = self.preprocess_text(text)

            # Парсим выражение
            try:
                expr = sp.sympify(cleaned_text)
            except Exception as e:
                return {'success': False, 'error': f'Ошибка парсинга выражения: {e}'}

            original = expr

            steps.append({
                'description': 'Математическая форма',
                'formula': sp.latex(expr),
                'details': 'Выражение преобразовано в математическую форму'
            })

            # Шаг 1: Раскрытие скобок
            expanded = expand(expr)
            if expanded != expr:
                steps.append({
                    'description': 'Раскрытие скобок',
                    'formula': sp.latex(expanded),
                    'details': 'Применен дистрибутивный закон'
                })
                expr = expanded

            # Шаг 2: Приведение подобных
            collected = collect(expr, self.x)
            if collected != expr:
                steps.append({
                    'description': 'Приведение подобных слагаемых',
                    'formula': sp.latex(collected),
                    'details': 'Сгруппированы подобные члены'
                })
                expr = collected

            # Шаг 3: Упрощение дробей
            simplified_frac = together(expr)
            if simplified_frac != expr:
                steps.append({
                    'description': 'Упрощение дробей',
                    'formula': sp.latex(simplified_frac),
                    'details': 'Дроби приведены к общему знаменателю'
                })
                expr = simplified_frac

            # Шаг 4: Тригонометрическое упрощение
            if any(func in str(expr) for func in ['sin', 'cos', 'tan', 'cot']):
                trig_simplified = trigsimp(expr)
                if trig_simplified != expr:
                    steps.append({
                        'description': 'Тригонометрическое упрощение',
                        'formula': sp.latex(trig_simplified),
                        'details': 'Применены тригонометрические тождества'
                    })
                    expr = trig_simplified

            # Шаг 5: Факторизация
            factored = factor(expr)
            if factored != expr:
                steps.append({
                    'description': 'Факторизация',
                    'formula': sp.latex(factored),
                    'details': 'Выражение разложено на множители'
                })
                expr = factored

            # Финальное упрощение
            final = simplify(expr)
            if final != expr:
                steps.append({
                    'description': 'Финальное упрощение',
                    'formula': sp.latex(final),
                    'details': 'Окончательное упрощение выражения'
                })
                expr = final

            steps.append({
                'description': 'Результат упрощения',
                'formula': sp.latex(expr),
                'details': 'Выражение упрощено'
            })

            return {
                'success': True,
                'solution': str(expr),
                'steps': steps,
                'problem_type': 'simplify',
                'processing_time': 0.2,
                'explanation': 'Выражение упрощено с использованием алгебраических преобразований'
            }

        except Exception as e:
            logger.error(f"Ошибка упрощения: {e}")
            return {'success': False, 'error': f'Ошибка упрощения: {e}'}

    def preprocess_text(self, text):
        """Предварительная обработка текста"""
        text = text.replace('^', '**')
        text = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', text)
        text = re.sub(r'([a-zA-Z])(\d)', r'\1*\2', text)
        return text