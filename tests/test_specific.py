"""
Тесты для конкретных сложных случаев
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import logging

logging.basicConfig(level=logging.DEBUG)

from solvers.trigonometric_solver import TrigonometricSolver
from solvers.derivative_solver import DerivativeSolver


def test_hard_trigonometric():
    """Тест сложных тригонометрических уравнений"""
    print("🧪 Тест сложных тригонометрических уравнений")
    print("=" * 50)

    solver = TrigonometricSolver()
    hard_cases = [
        "x + cos(x) = 1",
        "sin(x) + x = 2",
        "2*sin(x) - 3*cos(x) = 0"
    ]

    for test in hard_cases:
        print(f"\n🎯 {test}")
        result = solver.solve_with_steps(test)
        if result['success']:
            print(f"   ✅ Решение: {result['solution']}")
            print(f"   📊 Шагов: {len(result['steps'])}")
            # Покажем ключевые шаги
            for i, step in enumerate(result['steps'][-3:], 1):
                print(f"     {i}. {step.get('description', 'Нет описания')}")
        else:
            print(f"   ❌ Ошибка: {result.get('error', 'Неизвестно')}")


def test_complex_derivatives():
    """Тест сложных производных"""
    print("\n\n🧪 Тест сложных производных")
    print("=" * 50)

    solver = DerivativeSolver()
    complex_cases = [
        "производная sin(x)*cos(x)",
        "derivative of x^2 * e^x",
        "d/dx (x^2 * sin(x))"
    ]

    for test in complex_cases:
        print(f"\n🎯 {test}")
        result = solver.solve_with_steps(test)
        if result['success']:
            print(f"   ✅ Решение: {result['solution']}")
            print(f"   📊 Шагов: {len(result['steps'])}")
        else:
            print(f"   ❌ Ошибка: {result.get('error', 'Неизвестно')}")


if __name__ == "__main__":
    test_hard_trigonometric()
    test_complex_derivatives()