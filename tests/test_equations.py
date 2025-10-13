"""
Тесты уравнений
"""

import sys
import os
import sympy as sp
from sympy import parse_expr, simplify, expand, symbols

sys.path.append('..')

from math_solver import math_solver


def test_equations():
    print("📐 ТЕСТЫ УРАВНЕНИЙ")
    print("=" * 40)

    test_cases = [
        {"problem": "x + 3 = 7", "expected": "x = 4", "desc": "Простое уравнение"},
        {"problem": "2x + 5 = 13", "expected": "x = 4", "desc": "Уравнение с коэффициентом"},
        {"problem": "3x - 7 = 8", "expected": "x = 5", "desc": "Уравнение с вычитанием"},
        {"problem": "x/2 = 6", "expected": "x = 12", "desc": "Уравнение с делением"},
        {"problem": "x^2 = 16", "expected": "x = -4, x = 4", "desc": "Квадратное уравнение"},
        {"problem": "x^2 - 5x + 6 = 0", "expected": "x = 2, x = 3", "desc": "Квадратное уравнение 2"},
        {"problem": "2(x + 3) = 10", "expected": "x = 2", "desc": "Уравнение со скобками"},
        {"problem": "(x + 1)^2 = 9", "expected": "x = -4, x = 2", "desc": "Уравнение с квадратом"},
        {"problem": "sin(x) - 1/2 = 0", "expected": "x = pi/6, x = 5*pi/6", "desc": "sin(x)=0.5, периодическое решение"},
        {"problem": "cos(2*x) - 1/2 = 0", "expected": "x = pi/6, x = 5*pi/6", "desc": "cos(2x)=0.5"},
        {"problem": "tan(x) - 1 = 0", "expected": "x = pi/4", "desc": "tan(x)=1"},
        {"problem": "sin(x) + cos(x) - 1 = 0", "expected": "x = 0, x = pi/2", "desc": "Комбинированное тригонометрическое"},
        {"problem": "exp(x) - 5 = 0", "expected": "x = log(5)", "desc": "Экспоненциальное e^x=5"},
        {"problem": "log(x) - 3 = 0", "expected": "x = exp(3)", "desc": "Логарифм ln(x)=3"},
        {"problem": "log(x, 2) - 4 = 0", "expected": "x = 16", "desc": "log₂(x)=4"},
        {"problem": "x**3 - 6*x**2 + 11*x - 6 = 0", "expected": "x = 1, x = 2, x = 3", "desc": "Кубическое с 3 корнями"},
        {"problem": "x**4 - 5*x**2 + 4 = 0", "expected": "x = -2, x = -1, x = 1, x = 2", "desc": "Биквадратное уравнение"},
        {"problem": "sqrt(x + 2) - x = 0", "expected": "x = 2", "desc": "Радикальное, с ОДЗ"},
        {"problem": "x*exp(x) - 1 = 0", "expected": "x = LambertW(1)", "desc": "x·e^x=1 (Ламбертова W-функция)"},
        {"problem": "x**3 + 3*x**2 + 3*x + 1 = 0", "expected": "x = -1", "desc": "Полный куб (x+1)^3=0"},
        {"problem": "2**(x+1) - 8 = 0", "expected": "x = 2", "desc": "Показательное"},
        {"problem": "log(x - 1) + log(x + 1) = 0", "expected": "x = sqrt(2)", "desc": "Сумма логарифмов"},
        {"problem": "x**2 + 1 = 0", "expected": "x = -I, x = I", "desc": "Комплексные корни"}
    ]

    for test in test_cases:
        print(f"\n📝 {test['desc']}")
        print(f"   Задача: {test['problem']}")

        result = math_solver.solve_problem(test['problem'])

        if result['success']:
            solution_str = result['solution']
            expected_str = test['expected']

            # Сравниваем строковые представления
            if _solutions_equivalent(solution_str, expected_str):
                print(f"   ✅ УСПЕХ: {solution_str}")
            else:
                print(f"   ❌ ОШИБКА: {solution_str} != {expected_str}")
        else:
            print(f"   ❌ ОШИБКА: {result.get('error', 'Unknown error')}")

    def _solutions_equivalent(self, solution_str, expected_str):
        """
        Сравнивает два строковых представления решений на эквивалентность

        Args:
            solution_str: Решение от решателя (например "x = 4" или "Решения: x = 1, x = 2")
            expected_str: Ожидаемое решение (например "x = 4" или "x = 1, x = 2")

        Returns:
            True если решения математически эквивалентны
        """
        try:
            # Очищаем строки от лишних слов
            clean_solution = solution_str.replace('Решения: ', '').replace('Решение: ', '').strip()
            clean_expected = expected_str.strip()

            # Если решения идентичны
            if clean_solution == clean_expected:
                return True

            # Парсим решения и сравниваем математически
            x = symbols('x')

            # Извлекаем значения из solution_str
            solution_values = self._extract_solution_values(clean_solution)
            expected_values = self._extract_solution_values(clean_expected)

            # Сравниваем множества решений
            if set(solution_values) == set(expected_values):
                return True

            # Сравниваем математически через упрощение
            for sol_val in solution_values:
                for exp_val in expected_values:
                    if simplify(sol_val - exp_val) == 0:
                        return True

            return False

        except Exception as e:
            # Если не удалось сравнить математически, сравниваем как строки
            return solution_str == expected_str

    def _extract_solution_values(self, solution_str):
        """
        Извлекает числовые значения из строки решения

        Args:
            solution_str: Строка с решением (например "x = 4" или "x = 1, x = 2")

        Returns:
            Список значений
        """
        try:
            values = []
            # Разделяем по запятым и извлекаем значения после "x = "
            parts = solution_str.split(',')
            for part in parts:
                if '=' in part:
                    value_str = part.split('=')[1].strip()
                    values.append(parse_expr(value_str))
                else:
                    # Если нет "=", пробуем парсить как есть
                    values.append(parse_expr(part.strip()))
            return values
        except:
            return []


if __name__ == "__main__":
    test_equations()