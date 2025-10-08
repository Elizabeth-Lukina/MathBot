# -*- coding: utf-8 -*-
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
from sympy.plotting import plot
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
            cleaned_text = self._normalize_mathematical_text(problem_text)
            
            # Решаем в зависимости от типа
            result = None
            method = "sympy"
            
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
                # Пробуем общее решение
                result = self._solve_general(cleaned_text)
            
            processing_time = time.time() - start_time
            
            if result and result.get('solution'):
                return {
                    'success': True,
                    'problem_type': problem_type,
                    'solution': result['solution'],
                    'steps': result.get('steps', []),
                    'latex': result.get('latex', ''),
                    'method': method,
                    'processing_time': processing_time,
                    'explanation': result.get('explanation', '')
                }
            else:
                return {
                    'success': False,
                    'problem_type': problem_type,
                    'method': method,
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
        text_lower = text.lower().replace(' ', '')
        
        # Паттерны для разных типов задач
        patterns = {
            'integral': [
                r'∫', r'интеграл', r'проинтегрир', r'integrate',
                r'∫.*dx', r'∫.*dy', r'вычислить.*интеграл'
            ],
            'derivative': [
                r"производн", r"дифференц", r"найти.*f'", r"f'",
                r"dy/dx", r"d/dx", r"diff", r"производная"
            ],
            'equation': [
                r'уравнение', r'решить.*=', r'найти.*x.*=', r'solve',
                r'x.*=.*\d', r'\d.*=.*x', r'система.*уравнений'
            ],
            'trigonometry': [
                r'sin', r'cos', r'tan', r'tg', r'ctg', r'sec', r'csc',
                r'arcsin', r'arccos', r'arctan', r'тригонометр'
            ],
            'arithmetic': [
                r'вычислить', r'найти.*значение', r'упростить',
                r'calculate', r'compute', r'simplify'
            ],
            'algebra': [
                r'упростить.*выражение', r'разложить', r'factor',
                r'expand', r'алгебра'
            ]
        }
        
        for problem_type, type_patterns in patterns.items():
            for pattern in type_patterns:
                if re.search(pattern, text_lower):
                    return problem_type
        
        # По умолчанию считаем арифметикой
        return 'arithmetic'
    
    def _normalize_mathematical_text(self, text: str) -> str:
        """Нормализация математического текста для SymPy"""
        try:
            # Заменяем русские функции на английские
            replacements = {
                'син': 'sin',
                'кос': 'cos', 
                'тан': 'tan',
                'тг': 'tan',
                'котан': 'cot',
                'ктг': 'cot',
                'арксин': 'asin',
                'арккос': 'acos',
                'арктан': 'atan',
                'лог': 'log',
                'логарифм': 'log',
                'натуральный.*логарифм': 'ln',
                'корень': 'sqrt',
                'пи': 'pi',
                'е': 'E',
                'бесконечность': 'oo',
            }
            
            text_normalized = text
            for russian, english in replacements.items():
                text_normalized = re.sub(russian, english, text_normalized, flags=re.IGNORECASE)
            
            # Обрабатываем специальные символы
            text_normalized = text_normalized.replace('∞', 'oo')
            text_normalized = text_normalized.replace('π', 'pi')
            text_normalized = text_normalized.replace('²', '**2')
            text_normalized = text_normalized.replace('³', '**3')
            
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
            # Ищем знак равенства
            if '=' not in text:
                return None
            
            left_side, right_side = text.split('=', 1)
            
            # Парсим обе части уравнения
            left_expr = parse_expr(left_side.strip())
            right_expr = parse_expr(right_side.strip())
            
            # Создаем уравнение
            equation = sp.Eq(left_expr, right_expr)
            
            # Находим переменные
            variables = equation.free_symbols
            
            if not variables:
                return {'solution': 'Нет переменных для решения', 'steps': []}
            
            # Решаем уравнение
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
            # Ищем паттерны интегралов
            integral_pattern = r'∫\s*(.+?)\s*d([a-z])'
            match = re.search(integral_pattern, text)
            
            if match:
                integrand = match.group(1).strip()
                variable = match.group(2)
            else:
                # Пробуем найти выражение для интегрирования
                # Ищем выражение перед dx, dy и т.д.
                dx_pattern = r'(.+?)\s*d([xyz])'
                dx_match = re.search(dx_pattern, text)
                
                if dx_match:
                    integrand = dx_match.group(1).strip()
                    variable = dx_match.group(2)
                else:
                    # Берем все выражение и интегрируем по x
                    integrand = text
                    variable = 'x'
            
            # Парсим подынтегральное выражение
            expr = parse_expr(integrand)
            var = symbols(variable)
            
            # Вычисляем интеграл
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
                'explanation': f"Вычислен неопределенный интеграл от {integrand} по переменной {variable}"
            }
            
        except Exception as e:
            logger.error(f"Ошибка вычисления интеграла: {e}")
            return {'solution': '', 'steps': [], 'latex': '', 'explanation': ''}
    
    def _solve_derivative(self, text: str) -> Dict[str, Any]:
        """Решение производных"""
        try:
            # Ищем функцию для дифференцирования
            # Паттерны: f'(x), d/dx, производная от...
            
            # Удаляем ключевые слова
            text_clean = re.sub(r'(производная|дифференц|найти|от|по)', '', text, flags=re.IGNORECASE)
            text_clean = re.sub(r"f'|dy/dx|d/dx", '', text_clean)
            
            # Ищем функцию f(x) = ...
            func_pattern = r'f\s*\(\s*([a-z])\s*\)\s*=\s*(.+)'
            func_match = re.search(func_pattern, text)
            
            if func_match:
                variable = func_match.group(1)
                function_expr = func_match.group(2)
            else:
                # Берем всё выражение
                function_expr = text_clean.strip()
                variable = 'x'  # По умолчанию по x
            
            # Парсим выражение
            expr = parse_expr(function_expr)
            var = symbols(variable)
            
            # Вычисляем производную
            derivative_result = diff(expr, var)
            
            steps = [
                f"Функция: f({variable}) = {sp.latex(expr)}",
                f"Переменная: {variable}",
                f"Производная: d/d{variable}[{sp.latex(expr)}]",
                f"Результат: {sp.latex(derivative_result)}"
            ]
            
            return {
                'solution': str(derivative_result),
                'steps': steps,
                'latex': sp.latex(derivative_result),
                'explanation': f"Найдена производная функции {function_expr} по переменной {variable}"
            }
            
        except Exception as e:
            logger.error(f"Ошибка вычисления производной: {e}")
            return {'solution': '', 'steps': [], 'latex': '', 'explanation': ''}
    
    def _solve_trigonometry(self, text: str) -> Dict[str, Any]:
        """Решение тригонометрических задач"""
        try:
            # Нормализуем текст
            normalized_text = self._normalize_mathematical_text(text)
            
            # Парсим выражение
            expr = parse_expr(normalized_text)
            
            # Упрощаем тригонометрическое выражение
            simplified = sp.trigsimp(expr)
            
            # Если выражение содержит переменные, пробуем решить
            variables = expr.free_symbols
            result = simplified
            
            if variables:
                # Пробуем решить тригонометрическое уравнение
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
            # Парсим арифметическое выражение
            expr = parse_expr(text)
            
            # Вычисляем результат
            result = expr.evalf()
            
            steps = [
                f"Выражение: {sp.latex(expr)}",
                f"Вычисление: {result}"
            ]
            
            return {
                'solution': str(result),
                'steps': steps,
                'latex': sp.latex(result),
                'explanation': f"Выполнены арифметические вычисления"
            }
            
        except Exception as e:
            logger.error(f"Ошибка арифметических вычислений: {e}")
            return {'solution': '', 'steps': [], 'latex': '', 'explanation': ''}
    
    def _solve_algebra(self, text: str) -> Dict[str, Any]:
        """Решение алгебраических задач"""
        try:
            expr = parse_expr(text)
            
            # Пробуем различные алгебраические операции
            simplified = simplify(expr)
            expanded = expand(expr)
            factored = factor(expr)
            
            # Выбираем наиболее подходящий результат
            results = {
                'simplified': simplified,
                'expanded': expanded,
                'factored': factored
            }
            
            # Выбираем результат, отличный от исходного
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
            
            # Пробуем упростить выражение
            simplified = simplify(expr)
            
            # Если есть переменные, пробуем решить как уравнение
            variables = expr.free_symbols
            solutions = None
            
            if variables and '=' in text:
                try:
                    # Разделяем на части уравнения
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