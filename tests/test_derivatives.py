"""
Тесты производных
"""

import sys
import os

sys.path.append('..')

from math_solver import math_solver


def test_derivatives():
    print("📈 ТЕСТЫ ПРОИЗВОДНЫХ")
    print("=" * 40)

    test_cases = [
        {"problem": "найти производную: x^2", "expected": "2*x", "desc": "Простая производная"},
        {"problem": "производная от 3x^2 + 2x + 1", "expected": "6*x + 2", "desc": "Полином"},
        {"problem": "f(x) = x^3 - 2x", "expected": "3*x**2 - 2", "desc": "Функция f(x)"},
        {"problem": "дифференцировать sin(x)", "expected": "cos(x)", "desc": "Тригонометрическая функция"},
        {"problem": "производная e^x", "expected": "exp(x)", "desc": "Экспонента"},
        {"problem": "найти f'(x) для x^4", "expected": "4*x**3", "desc": "Степень 4"},
        {"problem": "производная cos(x)", "expected": "-sin(x)", "desc": "Косинус"},
        {"problem": "f(x) = ln(x)", "expected": "1/x", "desc": "Логарифм"},
    ]

    for test in test_cases:
        print(f"\n📝 {test['desc']}")
        print(f"   Задача: {test['problem']}")

        result = math_solver.solve_problem(test['problem'])

        if result['success']:
            if test['expected'] in str(result['solution']):
                print(f"   ✅ УСПЕХ: {result['solution']}")
            else:
                print(f"   ❌ ОШИБКА: {result['solution']} != {test['expected']}")
        else:
            print(f"   ❌ ОШИБКА: {result.get('error', 'Unknown error')}")


if __name__ == "__main__":
    test_derivatives()