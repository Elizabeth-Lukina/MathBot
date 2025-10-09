"""
Тесты интегралов
"""

import sys
import os

sys.path.append('..')

from math_solver import math_solver


def test_integrals():
    print("∫ ТЕСТЫ ИНТЕГРАЛОВ")
    print("=" * 40)

    test_cases = [
        {"problem": "∫x dx", "expected": "x**2/2", "desc": "Простой интеграл"},
        {"problem": "интеграл от 2x", "expected": "x**2", "desc": "Интеграл с коэффициентом"},
        {"problem": "∫(x^2 + 1) dx", "expected": "x**3/3 + x", "desc": "Полином"},
        {"problem": "проинтегрировать sin(x)", "expected": "-cos(x)", "desc": "Тригонометрический"},
        {"problem": "∫e^x dx", "expected": "exp(x)", "desc": "Экспонента"},
        {"problem": "∫(3x^2 + 2x) dx", "expected": "x**3 + x**2", "desc": "Полином 2"},
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
    test_integrals()