"""
Тесты уравнений
"""

import sys
import os
import sympy as sp
from sympy import parse_expr, simplify, symbols, pi, I

sys.path.append('..')

from math_solver import math_solver


def test_equations():
    print("📐 ТЕСТЫ УРАВНЕНИЙ")
    print("=" * 40)

    test_cases = [
        {"problem": "x + 3 = 7", "expected": "[4]", "desc": "Простое уравнение"},
        {"problem": "2x + 5 = 13", "expected": "[4]", "desc": "Уравнение с коэффициентом"},
        {"problem": "3x - 7 = 8", "expected": "[5]", "desc": "Уравнение с вычитанием"},
        {"problem": "x/2 = 6", "expected": "[12]", "desc": "Уравнение с делением"},
        {"problem": "x^2 = 16", "expected": "[-4, 4]", "desc": "Квадратное уравнение"},
        {"problem": "x^2 - 5x + 6 = 0", "expected": "[2, 3]", "desc": "Квадратное уравнение 2"},
        {"problem": "2(x + 3) = 10", "expected": "[2]", "desc": "Уравнение со скобками"},
        {"problem": "(x + 1)^2 = 9", "expected": "[-4, 2]", "desc": "Уравнение с квадратом"},
        # Тригонометрические - проверяем основные корни
        {"problem": "sin(x) - 1/2 = 0", "expected_check": "pi/6", "desc": "sin(x)=0.5, периодическое решение"},
        {"problem": "cos(2*x) - 1/2 = 0", "expected_check": "pi/6", "desc": "cos(2x)=0.5"},
        {"problem": "tan(x) - 1 = 0", "expected_check": "pi/4", "desc": "tan(x)=1"},
        {"problem": "sin(x) + cos(x) - 1 = 0", "expected_check": "2*_n*pi", "desc": "Комбинированное тригонометрическое"},
        # Остальные тесты
        {"problem": "exp(x) - 5 = 0", "expected": "[log(5)]", "desc": "Экспоненциальное e^x=5"},
        {"problem": "log(x) - 3 = 0", "expected": "[exp(3)]", "desc": "Логарифм ln(x)=3"},
        {"problem": "log(x, 2) - 4 = 0", "expected": "[16]", "desc": "log₂(x)=4"},
        {"problem": "x**3 - 6*x**2 + 11*x - 6 = 0", "expected": "[1, 2, 3]", "desc": "Кубическое с 3 корнями"},
        {"problem": "x**4 - 5*x**2 + 4 = 0", "expected": "[-2, -1, 1, 2]", "desc": "Биквадратное уравнение"},
        {"problem": "sqrt(x + 2) - x = 0", "expected": "[2]", "desc": "Радикальное, с ОДЗ"},
        {"problem": "x*exp(x) - 1 = 0", "expected_check": "LambertW", "desc": "x·e^x=1 (Ламбертова W-функция)"},
        {"problem": "x**3 + 3*x**2 + 3*x + 1 = 0", "expected": "[-1]", "desc": "Полный куб (x+1)^3=0"},
        {"problem": "2**(x+1) - 8 = 0", "expected": "[2]", "desc": "Показательное"},
        {"problem": "log(x - 1) + log(x + 1) = 0", "expected_check": "sqrt(2)", "desc": "Сумма логарифмов"},
        {"problem": "x**2 + 1 = 0", "expected_check": "I", "desc": "Комплексные корни"},
    ]

    for test in test_cases:
        print(f"\n📝 {test['desc']}")
        print(f"   Задача: {test['problem']}")

        result = math_solver.solve_problem(test['problem'])

        if result['success']:
            solution_str = str(result['solution'])

            # Разные типы проверок
            if 'expected_check' in test:
                # Проверяем, что ожидаемая подстрока есть в решении
                if test['expected_check'] in solution_str:
                    print(f"   ✅ УСПЕХ: {result['solution']}")
                else:
                    print(f"   ❌ ОШИБКА: {result['solution']} не содержит {test['expected_check']}")
            else:
                # Стандартная проверка
                if test['expected'] in solution_str:
                    print(f"   ✅ УСПЕХ: {result['solution']}")
                else:
                    print(f"   ❌ ОШИБКА: {result['solution']} != {test['expected']}")
        else:
            print(f"   ❌ ОШИБКА: {result.get('error', 'Unknown error')}")


if __name__ == "__main__":
    test_equations()