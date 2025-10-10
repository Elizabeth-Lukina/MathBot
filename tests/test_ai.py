"""
Тестирование AI объяснений
"""

import sys
import os

sys.path.append('.')

from hybrid_solver import hybrid_solver


def test_ai_explanation():
    """Тестируем генерацию AI объяснений"""

    test_problems = [
        "найти производную f(x) = x^2 * sin(x)",
        "производная от x^2 + 3x - 5",
        "интеграл sin(x) dx"
    ]

    for problem in test_problems:
        print(f"\n{'=' * 50}")
        print(f"🔍 ТЕСТ: {problem}")
        print(f"{'=' * 50}")

        # Тестируем все режимы
        for mode in ['quick', 'exam', 'tutor']:
            print(f"\n📋 РЕЖИМ: {mode}")
            result = hybrid_solver.solve_with_mode(problem, mode)

            print(f"✅ Успех: {result['success']}")
            print(f"🔧 Источник: {result.get('source', 'unknown')}")

            if result['success']:
                print(f"📝 Объяснение:\n{result['explanation']}")
            else:
                print(f"❌ Ошибка: {result.get('error', 'Unknown error')}")

            if result.get('ai_error'):
                print(f"🤖 AI ошибка: {result['ai_error']}")


if __name__ == "__main__":
    test_ai_explanation()