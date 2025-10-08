"""
Модуль для решения математических задач
Использует SymPy для символьных вычислений и определения типов задач
"""

import sympy as sp
import logging
import re
import time
from typing import Dict, List, Optional, Tuple, Any
from sympy import symbols, solve, integrate, diff, simplify, expand, factor
from sympy import sin, cos, tan, log, exp, sqrt, pi, oo, I
from sympy.parsing.sympy_parser import parse_expr
from config import SUPPORTED_MATH_TYPES

logger = logging.getLogger(__name__)

class MathSolver:
    """Класс для решения математических задач с помощью SymPy"""

    def __init__(self):
        # Общие переменные для вычислений
        self.common_vars = symbols('x y z t a b c n k')
        self.x, self.y, self.z, self.t = symbols('x y z t')
        self.a, self.b, self.c = symbols('a b c')

    def solve_problem(self, problem_text: str) -> Dict[str, Any]:
        """
        Основная функция решения математической задачи
        """
        start_time = time.time()

        try:
            logger.info(f"=== НОВАЯ ЗАДАЧА: {problem_text} ===")

            # Определяем тип задачи
            problem_type = self._detect_problem_type(problem_text)
            logger.info(f"Определен тип задачи: {problem_type}")

            # Очищаем и нормализуем текст
            cleaned_text = self._normalize_mathematical_text(problem_text)

            # Решаем в зависимости от типа
            result = None

            if problem_type == "equation":
                result = self._solve_equation(cleaned_text)
            elif problem_type == "integral":
                result = self._solve_integral(cleaned_text)
            elif problem_type == "derivative":
                result = self._solve_derivative(cleaned_text)
            elif problem_type == "trigonometry":
                result = self._solve_trigonometry(cleaned_text)
            elif problem_type == "arithmetic":
                result = self._solve_arithmetic(cleaned_text)
            elif problem_type == "algebra":
                result = self._solve_algebra(cleaned_text)
            else:
                result = self._solve_general(cleaned_text)

            processing_time = time.time() - start_time

            if result and result.get('solution'):
                return {
                    'success': True,
                    'problem_type': problem_type,
                    'solution': result['solution'],
                    'steps': result.get('steps', []),
                    'latex': result.get('latex', ''),
                    'method': 'sympy',
                    'processing_time': processing_time,
                    'explanation': result.get('explanation', '')
                }
            else:
                return {
                    'success': False,
                    'problem_type': problem_type,
                    'method': 'sympy',
                    'processing_time': processing_time,
                    'error': 'Не удалось решить задачу с помощью SymPy'
                }

        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Ошибка решения задачи: {e}")
            return {
                'success': False,
                'method': 'sympy',
                'processing_time': processing_time,
                'error': str(e)
            }

    def _detect_problem_type(self, text: str) -> str:
        """Определение типа математической задачи"""
        text_lower = text.lower()

        # Сначала проверяем производные (более специфично)
        if any(word in text_lower for word in ['производн', 'дифференц', 'f\'', 'd/dx', 'dy/dx']):
            return 'derivative'

        # Добавляем проверку на f(x) = выражение - это тоже производная
        if re.search(r'f\s*\(\s*x\s*\)\s*=', text, re.IGNORECASE):
            return 'derivative'

        # Потом интегралы
        if any(word in text_lower for word in ['интеграл', '∫', 'проинтегрир']):
            return 'integral'

        # Потом уравнения
        if '=' in text:
            return 'equation'

        # Потом тригонометрию
        if any(word in text_lower for word in ['sin', 'cos', 'tan', 'tg', 'ctg', 'тригонометр']):
            return 'trigonometry'

        # Потом алгебру
        if any(word in text_lower for word in ['упростить', 'разложить', 'алгебр']):
            return 'algebra'

        return 'arithmetic'

    def _normalize_mathematical_text(self, text: str) -> str:
        """Нормализация математического текста для SymPy"""
        try:
            replacements = {
                'син': 'sin', 'кос': 'cos', 'тан': 'tan', 'тг': 'tan',
                'котан': 'cot', 'ктг': 'cot', 'арксин': 'asin', 'арккос': 'acos',
                'арктан': 'atan', 'лог': 'log', 'логарифм': 'log',
                'натуральный.*логарифм': 'ln', 'корень': 'sqrt', 'пи': 'pi',
                'е': 'E', 'бесконечность': 'oo',
            }

            text_normalized = text
            for russian, english in replacements.items():
                text_normalized = re.sub(russian, english, text_normalized, flags=re.IGNORECASE)

            # Обрабатываем специальные символы
            text_normalized = text_normalized.replace('∞', 'oo')
            text_normalized = text_normalized.replace('π', 'pi')
            text_normalized = text_normalized.replace('²', '**2')
            text_normalized = text_normalized.replace('³', '**3')
            text_normalized = text_normalized.replace('^', '**')

            # Добавляем знаки умножения где нужно
            text_normalized = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', text_normalized)
            text_normalized = re.sub(r'([a-zA-Z])(\d)', r'\1*\2', text_normalized)
            text_normalized = re.sub(r'(\))(\()', r')\1*\2', text_normalized)

            return text_normalized.strip()

        except Exception as e:
            logger.error(f"Ошибка нормализации текста: {e}")
            return text

    def _solve_equation(self, text: str) -> Dict[str, Any]:
        """Решение уравнений"""
        try:
            if '=' not in text:
                return None

            left_side, right_side = text.split('=', 1)
            logger.info(f"Левая часть: '{left_side}', Правая часть: '{right_side}'")

            left_expr = parse_expr(left_side.strip())
            right_expr = parse_expr(right_side.strip())

            equation = sp.Eq(left_expr, right_expr)
            variables = equation.free_symbols

            if not variables:
                return {'solution': 'Нет переменных для решения', 'steps': []}

            solutions = solve(equation, list(variables))

            steps = [
                f"Уравнение: {sp.latex(equation)}",
                f"Переменные: {', '.join(str(var) for var in variables)}",
                f"Решение: {solutions}"
            ]

            latex_solution = sp.latex(solutions) if solutions else "Нет решений"

            return {
                'solution': str(solutions),
                'steps': steps,
                'latex': latex_solution,
                'explanation': f"Решено уравнение с переменными: {', '.join(str(var) for var in variables)}"
            }

        except Exception as e:
            logger.error(f"Ошибка решения уравнения: {e}")
            return {'solution': '', 'steps': [], 'latex': '', 'explanation': ''}

    def _solve_integral(self, text: str) -> Dict[str, Any]:
        """Решение интегралов"""
        try:
            integral_pattern = r'∫\s*(.+?)\s*d([a-z])'
            match = re.search(integral_pattern, text)

            if match:
                integrand = match.group(1).strip()
                variable = match.group(2)
            else:
                dx_pattern = r'(.+?)\s*d([xyz])'
                dx_match = re.search(dx_pattern, text)

                if dx_match:
                    integrand = dx_match.group(1).strip()
                    variable = dx_match.group(2)
                else:
                    integrand = text
                    variable = 'x'

            expr = parse_expr(integrand)
            var = symbols(variable)
            integral_result = integrate(expr, var)

            steps = [
                f"Подынтегральное выражение: {sp.latex(expr)}",
                f"Переменная интегрирования: {variable}",
                f"Интеграл: ∫{sp.latex(expr)} d{variable}",
                f"Результат: {sp.latex(integral_result)} + C"
            ]

            return {
                'solution': str(integral_result) + ' + C',
                'steps': steps,
                'latex': sp.latex(integral_result) + ' + C',
                'explanation': f"Вычислен неопределенный интеграл"
            }

        except Exception as e:
            logger.error(f"Ошибка вычисления интеграла: {e}")
            return {'solution': '', 'steps': [], 'latex': '', 'explanation': ''}

    def _solve_derivative(self, text: str) -> Dict[str, Any]:
        """Решение производных"""
        try:
            logger.info(f"Обрабатываем производную: {text}")

            clean_text = text.lower()
            clean_text = re.sub(r'(производная|производную|найти|функции|функция|от|дифференцировать|дифференциал)', '', clean_text)
            clean_text = clean_text.strip()

            expression = None

            match1 = re.search(r'f\s*\(\s*x\s*\)\s*=\s*(.+)', text, re.IGNORECASE)
            if match1:
                expression = match1.group(1).strip()
                logger.info(f"Нашли выражение по паттерну f(x): {expression}")

            if not expression:
                math_pattern = r'([x\d+\-*/\^\.\s\(\)]+)'
                matches = re.findall(math_pattern, clean_text)
                if matches:
                    expression = matches[-1].strip()
                    logger.info(f"Нашли выражение по математическому паттерну: {expression}")

            if not expression:
                expression = clean_text
                logger.info(f"Берем весь очищенный текст: {expression}")

            if not expression:
                return {'solution': '', 'steps': [], 'latex': '', 'explanation': 'Не найдено выражение для дифференцирования'}

            expression = self._normalize_mathematical_text(expression)
            logger.info(f"Нормализованное выражение: {expression}")

            expression = expression.replace('^', '**')

            try:
                expr = parse_expr(expression)
            except Exception as e:
                logger.error(f"Ошибка парсинга выражения '{expression}': {e}")
                return {'solution': '', 'steps': [], 'latex': '', 'explanation': f'Ошибка парсинга выражения: {e}'}

            variables = expr.free_symbols
            if not variables:
                return {'solution': '', 'steps': [], 'latex': '', 'explanation': 'Нет переменных для дифференцирования'}

            var = list(variables)[0]
            derivative = diff(expr, var)

            steps = [
                f"Исходная функция: {sp.latex(expr)}",
                f"Переменная дифференцирования: {var}",
                f"Производная: {sp.latex(derivative)}"
            ]

            return {
                'solution': str(derivative),
                'steps': steps,
                'latex': sp.latex(derivative),
                'explanation': f"Найдена производная по переменной {var}"
            }

        except Exception as e:
            logger.error(f"Ошибка вычисления производной: {e}")
            return {'solution': '', 'steps': [], 'latex': '', 'explanation': f'Ошибка вычисления: {e}'}

    def _solve_trigonometry(self, text: str) -> Dict[str, Any]:
        """Решение тригонометрических задач"""
        try:
            normalized_text = self._normalize_mathematical_text(text)
            expr = parse_expr(normalized_text)
            simplified = sp.trigsimp(expr)

            variables = expr.free_symbols
            result = simplified

            if variables:
                try:
                    solutions = solve(expr, list(variables))
                    if solutions:
                        result = solutions
                except:
                    pass

            steps = [
                f"Исходное выражение: {sp.latex(expr)}",
                f"Упрощенное выражение: {sp.latex(simplified)}"
            ]

            if isinstance(result, list) and result:
                steps.append(f"Решения: {[sp.latex(sol) for sol in result]}")

            return {
                'solution': str(result),
                'steps': steps,
                'latex': sp.latex(result),
                'explanation': f"Решена тригонометрическая задача"
            }

        except Exception as e:
            logger.error(f"Ошибка решения тригонометрии: {e}")
            return {'solution': '', 'steps': [], 'latex': '', 'explanation': ''}

    def _solve_arithmetic(self, text: str) -> Dict[str, Any]:
        """Решение арифметических задач"""
        try:
            text = self._clean_arithmetic_text(text)

            try:
                result = eval(text)
                steps = [f"Вычисление: {text} = {result}"]
                return {
                    'solution': str(result),
                    'steps': steps,
                    'latex': str(result),
                    'explanation': "Выполнены арифметические вычисления"
                }
            except:
                return {
                    'solution': text,
                    'steps': ["Не удалось вычислить выражение"],
                    'latex': text,
                    'explanation': "Выражение требует ручного решения"
                }

        except Exception as e:
            logger.error(f"Ошибка арифметических вычислений: {e}")
            return {'solution': text, 'steps': [], 'latex': text, 'explanation': ''}

    def _clean_arithmetic_text(self, text: str) -> str:
        """Очистка арифметического текста"""
        text = re.sub(r'[^\d+\-*/()., ]', '', text)
        text = text.replace(',', '.')
        text = ' '.join(text.split())
        return text.strip()

    def _solve_algebra(self, text: str) -> Dict[str, Any]:
        """Решение алгебраических задач"""
        try:
            # Убираем слово "упростить" перед парсингом
            clean_text = re.sub(r'упростить\s*', '', text, flags=re.IGNORECASE)
            clean_text = re.sub(r'разложить\s*', '', clean_text, flags=re.IGNORECASE)

            expr = parse_expr(clean_text)
            simplified = simplify(expr)
            expanded = expand(expr)
            factored = factor(expr)

            result = simplified
            operation = 'упрощение'

            if expanded != expr:
                result = expanded
                operation = 'раскрытие скобок'
            elif factored != expr:
                result = factored
                operation = 'факторизация'

            steps = [
                f"Исходное выражение: {sp.latex(expr)}",
                f"Операция: {operation}",
                f"Результат: {sp.latex(result)}"
            ]

            return {
                'solution': str(result),
                'steps': steps,
                'latex': sp.latex(result),
                'explanation': f"Выполнено {operation} алгебраического выражения"
            }

        except Exception as e:
            logger.error(f"Ошибка алгебраических вычислений: {e}")
            return {'solution': '', 'steps': [], 'latex': '', 'explanation': ''}

    def _solve_general(self, text: str) -> Dict[str, Any]:
        """Общий решатель для неопределенных задач"""
        try:
            expr = parse_expr(text)
            simplified = simplify(expr)

            variables = expr.free_symbols
            solutions = None

            if variables and '=' in text:
                try:
                    parts = text.split('=')
                    if len(parts) == 2:
                        left = parse_expr(parts[0])
                        right = parse_expr(parts[1])
                        equation = sp.Eq(left, right)
                        solutions = solve(equation, list(variables))
                except:
                    pass
            
            result = solutions if solutions else simplified
            
            steps = [
                f"Выражение: {sp.latex(expr)}",
                f"Упрощение: {sp.latex(simplified)}"
            ]
            
            if solutions:
                steps.append(f"Решения: {solutions}")
            
            return {
                'solution': str(result),
                'steps': steps,
                'latex': sp.latex(result),
                'explanation': "Выполнена общая обработка математического выражения"
            }
            
        except Exception as e:
            logger.error(f"Ошибка общего решения: {e}")
            return {'solution': '', 'steps': [], 'latex': '', 'explanation': ''}

# Создаем глобальный экземпляр решателя
math_solver = MathSolver()