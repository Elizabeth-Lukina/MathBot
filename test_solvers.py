"""
Тесты для математических решателей
Проверяем, что SymPy правильно решает базовые задачи
"""

import sys
import os

sys.path.append(os.path.dirname(__file__))

from math_solver import math_solver
from hybrid_solver import hybrid_solver


def test_math_solver():
    """Тестируем базовый MathSolver"""
    print("🧪 Тестируем MathSolver...")

    test_cases = [
        {
            "problem": "2x + 5 = 13",
            "expected_type": "equation",
            "description": "Простое уравнение"
        },
        {
            "problem": "x + 3 = 7",
            "expected_type": "equation",
            "description": "Уравнение с x"
        },
        {
            "problem": "найти производную: x**2 + 3x",
            "expected_type": "derivative",
            "description": "Производная"
        },
        {
            "problem": "f(x) = x**2 + 1",
            "expected_type": "derivative",
            "description": "Функция для дифференцирования"
        },
        {
            "problem": "2 + 2 * 2",
            "expected_type": "arithmetic",
            "description": "Арифметика"
        },
        {
            "problem": "упростить (x+1)**2",
            "expected_type": "algebra",
            "description": "Алгебраическое упрощение"
        }
    ]

    passed = 0
    failed = 0

    for test in test_cases:
        print(f"\n📝 Тест: {test['description']}")
        print(f"Задача: {test['problem']}")

        result = math_solver.solve_problem(test['problem'])

        print(f"✅ Успех: {result['success']}")
        print(f"📊 Тип: {result.get('problem_type', 'N/A')} (ожидался: {test['expected_type']})")

        if result['success']:
            print(f"🎯 Решение: {result['solution']}")
            print(f"⏱ Время: {result['processing_time']:.3f}с")
            passed += 1
        else:
            print(f"❌ Ошибка: {result.get('error', 'Unknown error')}")
            failed += 1

        # Проверяем тип задачи
        if result.get('problem_type') == test['expected_type']:
            print("✅ Тип задачи определен верно")
        else:
            print(f"❌ Тип задачи не совпадает: {result.get('problem_type')} != {test['expected_type']}")

    print(f"\n📊 Итог MathSolver: {passed}/{len(test_cases)} пройдено")
    return passed, failed


def test_hybrid_solver():
    """Тестируем HybridSolver"""
    print("\n\n🧪 Тестируем HybridSolver...")

    test_cases = [
        {
            "problem": "2x + 5 = 13",
            "mode": "quick",
            "description": "Быстрый режим - уравнение"
        },
        {
            "problem": "x + 3 = 7",
            "mode": "exam",
            "description": "Экзамен режим - уравнение"
        },
        {
            "problem": "найти производную: x**2",
            "mode": "exam",
            "description": "Производная в режиме экзамен"
        }
    ]

    passed = 0
    failed = 0

    for test in test_cases:
        print(f"\n📝 Тест: {test['description']}")
        print(f"Задача: {test['problem']}")
        print(f"Режим: {test['mode']}")

        result = hybrid_solver.solve_with_mode(test['problem'], test['mode'])

        print(f"✅ Успех: {result['success']}")
        print(f"🔧 Источник: {result.get('source', 'N/A')}")

        if result['success']:
            print(f"🎯 Решение: {result['solution']}")
            print(f"💡 Объяснение: {result.get('explanation', 'N/A')[:100]}...")
            print(f"⏱ Время: {result['processing_time']:.3f}с")
            passed += 1
        else:
            print(f"❌ Ошибка: {result.get('error', 'Unknown error')}")
            failed += 1

    print(f"\n📊 Итог HybridSolver: {passed}/{len(test_cases)} пройдено")
    return passed, failed


def test_specific_problems():
    """Тестируем конкретные проблемные случаи"""
    print("\n\n🔍 Тестируем проблемные случаи...")

    problems = [
        "найти производную: f(x) = x² + 3x - 5",
        "решить уравнение: 2x + 5 = 13",
        "f(x) = x**2 + 3*x - 5",
        "производная от x^2 + 3x - 5"
    ]

    for problem in problems:
        print(f"\n🔍 Проблема: {problem}")

        # Тестируем MathSolver
        math_result = math_solver.solve_problem(problem)
        print(f"MathSolver: {math_result['success']} - {math_result.get('solution', 'N/A')}")

        # Тестируем HybridSolver
        hybrid_result = hybrid_solver.solve_with_mode(problem, 'exam')
        print(f"HybridSolver: {hybrid_result['success']} - {hybrid_result.get('source', 'N/A')}")


if __name__ == "__main__":
    print("🚀 Запуск теста")


    math_passed, math_failed = test_math_solver()
    hybrid_passed, hybrid_failed = test_hybrid_solver()

    # Тестируем проблемные случаи
    test_specific_problems()

    print(f"\n🎯 ФИНАЛЬНЫЙ ИТОГ:")
    print(f"MathSolver: {math_passed} пройдено, {math_failed} упало")
    print(f"HybridSolver: {hybrid_passed} пройдено, {hybrid_failed} упало")

    if math_failed == 0 and hybrid_failed == 0:
        print("Все тесты пройдены!")
    else:
        print("Есть проблемы!")