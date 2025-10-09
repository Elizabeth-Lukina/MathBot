"""
Тесты арифметических выражений
"""

import sys
import os

sys.path.append('..')

from math_solver import math_solver


def test_arithmetic():
    print("🔢 ТЕСТЫ АРИФМЕТИКИ")
    print("=" * 40)

    test_cases = [
        {"problem": "2 + 2", "expected": "4", "desc": "Простое сложение"},
        {"problem": "10 - 5", "expected": "5", "desc": "Вычитание"},
        {"problem": "3 * 4", "expected": "12", "desc": "Умножение"},
        {"problem": "15 / 3", "expected": "5.0", "desc": "Деление"},
        {"problem": "2 + 3 * 4", "expected": "14", "desc": "Приоритет операций"},
        {"problem": "(2 + 3) * 4", "expected": "20", "desc": "Скобки"},
        {"problem": "2 ** 3", "expected": "8", "desc": "Степень"},
        {"problem": "sqrt(16)", "expected": "4", "desc": "Корень"},
        {"problem": "2.5 + 3.7", "expected": "6.2", "desc": "Десятичные числа"},
        {"problem": "(1 + 2) * (3 + 4)", "expected": "21", "desc": "Сложные скобки"},
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
    test_arithmetic()