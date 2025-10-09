"""
Тесты уравнений
"""

import sys
import os

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
    test_equations()