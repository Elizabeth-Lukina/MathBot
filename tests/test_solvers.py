"""
Тесты для всех решателей
"""

import sys
import os
import logging

from solvers.trigonometric_solver import TrigonometricSolver
from solvers.derivative_solver import DerivativeSolver
from solvers.equation_solver import EquationSolver
from solvers.integral_solver import IntegralSolver
from solvers.system_solver import SystemSolver
from solvers.simplify_solver import SimplifySolver

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
logging.basicConfig(level=logging.INFO)


def test_equation_solver():
    """Тест решателя уравнений"""
    print("🧪 Тест EquationSolver")
    print("=" * 40)

    solver = EquationSolver()
    test_cases = [
        "2x + 3 = 7",
        "x^2 - 4 = 0",
        "3x - 5 = 10"
    ]

    for test in test_cases:
        print(f"\n🔹 {test}")
        result = solver.solve_with_steps(test)
        if result['success']:
            print(f"   ✅ {result['solution']}")
            print(f"   📊 Шагов: {len(result['steps'])}")
        else:
            print(f"   ❌ {result.get('error', 'Ошибка')}")


def test_integral_solver():
    """Тест решателя интегралов"""
    print("\n\n🧪 Тест IntegralSolver")
    print("=" * 40)

    solver = IntegralSolver()
    test_cases = [
        "∫x^2 dx",
        "∫sin(x) dx",
        "∫(2x + 3) dx"
    ]

    for test in test_cases:
        print(f"\n🔹 {test}")
        result = solver.solve_with_steps(test)
        if result['success']:
            print(f"   ✅ {result['solution']}")
            print(f"   📊 Шагов: {len(result['steps'])}")
        else:
            print(f"   ❌ {result.get('error', 'Ошибка')}")


def test_derivative_solver():
    """Тест решателя производных"""
    print("\n\n🧪 Тест DerivativeSolver")
    print("=" * 40)

    solver = DerivativeSolver()
    test_cases = [
        "производная x^2",
        "derivative of sin(x)",
        "d/dx (3x^2 + 2x + 1)"
    ]

    for test in test_cases:
        print(f"\n🔹 {test}")
        result = solver.solve_with_steps(test)
        if result['success']:
            print(f"   ✅ {result['solution']}")
            print(f"   📊 Шагов: {len(result['steps'])}")
        else:
            print(f"   ❌ {result.get('error', 'Ошибка')}")


def test_trigonometric_solver():
    """Тест решателя тригонометрических уравнений"""
    print("\n\n🧪 Тест TrigonometricSolver")
    print("=" * 40)

    solver = TrigonometricSolver()
    test_cases = [
        "sin(x) = 0.5",
        "2*cos(x) = 1",
        "tan(x) = 1"
    ]

    for test in test_cases:
        print(f"\n🔹 {test}")
        result = solver.solve_with_steps(test)
        if result['success']:
            print(f"   ✅ {result['solution']}")
            print(f"   📊 Шагов: {len(result['steps'])}")
        else:
            print(f"   ❌ {result.get('error', 'Ошибка')}")


def test_system_solver():
    """Тест решателя систем уравнений"""
    print("\n\n🧪 Тест SystemSolver")
    print("=" * 40)

    solver = SystemSolver()
    test_cases = [
        "x + y = 5\n2x - y = 1",
        "x = 2y; y = x - 1"
    ]

    for test in test_cases:
        print(f"\n🔹 Система:")
        print(f"   {test}")
        result = solver.solve_with_steps(test)
        if result['success']:
            print(f"   ✅ {result['solution']}")
            print(f"   📊 Шагов: {len(result['steps'])}")
        else:
            print(f"   ❌ {result.get('error', 'Ошибка')}")


def test_simplify_solver():
    """Тест решателя упрощения"""
    print("\n\n🧪 Тест SimplifySolver")
    print("=" * 40)

    solver = SimplifySolver()
    test_cases = [
        "(x + 1)^2",
        "2x + 3x - x",
        "sin(x)^2 + cos(x)^2"
    ]

    for test in test_cases:
        print(f"\n🔹 {test}")
        result = solver.solve_with_steps(test)
        if result['success']:
            print(f"   ✅ {result['solution']}")
            print(f"   📊 Шагов: {len(result['steps'])}")
        else:
            print(f"   ❌ {result.get('error', 'Ошибка')}")


def run_all_tests():
    """Запуск всех тестов"""
    print("🚀 ЗАПУСК ВСЕХ ТЕСТОВ РЕШАТЕЛЕЙ")
    print("=" * 60)

    test_equation_solver()
    test_integral_solver()
    test_derivative_solver()
    test_trigonometric_solver()
    test_system_solver()
    test_simplify_solver()

    print("\n" + "=" * 60)
    print("✅ Все тесты завершены!")


if __name__ == "__main__":
    run_all_tests()
