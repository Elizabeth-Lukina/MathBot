"""
Тесты тригонометрии
"""

import sys
import os

sys.path.append('..')

from math_solver import math_solver


def test_trigonometry():
    print("📊 ТЕСТЫ ТРИГОНОМЕТРИИ")
    print("=" * 40)

    test_cases = [
        {"problem": "sin(0)", "expected": "0", "desc": "Синус 0"},
        {"problem": "cos(0)", "expected": "1", "desc": "Косинус 0"},
        {"problem": "sin(pi/2)", "expected": "1", "desc": "Синус pi/2"},
        {"problem": "cos(pi)", "expected": "-1", "desc": "Косинус pi"},
        {"problem": "tan(0)", "expected": "0", "desc": "Тангенс 0"},
        {"problem": "sin(pi/6)", "expected": "1/2", "desc": "Синус 30°"},
        {"problem": "cos(pi/3)", "expected": "1/2", "desc": "Косинус 60°"},
        {"problem": "упростить sin(x)^2 + cos(x)^2", "expected": "1", "desc": "Тригонометрическое тождество"},
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
    test_trigonometry()