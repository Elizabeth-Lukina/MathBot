"""
Тесты алгебраических преобразований
"""

import sys
import os

sys.path.append('..')

from math_solver import math_solver


def test_algebra():
    print("📐 ТЕСТЫ АЛГЕБРЫ")
    print("=" * 40)

    test_cases = [
        {"problem": "упростить (x + 1)^2", "expected": "x**2 + 2*x + 1", "desc": "Квадрат суммы"},
        {"problem": "разложить x^2 - 4", "expected": "(x - 2)*(x + 2)", "desc": "Разность квадратов"},
        {"problem": "упростить 2*(x + 3)", "expected": "2*x + 6", "desc": "Распределительный закон"},
        {"problem": "разложить x^2 + 2x + 1", "expected": "(x + 1)**2", "desc": "Квадрат суммы"},
        {"problem": "упростить (a + b)^3", "expected": "a**3 + 3*a**2*b + 3*a*b**2 + b**3", "desc": "Куб суммы"},
        {"problem": "разложить x^3 - 8", "expected": "(x - 2)*(x**2 + 2*x + 4)", "desc": "Разность кубов"},
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
    test_algebra()