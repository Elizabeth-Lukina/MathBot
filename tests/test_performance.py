"""
Тесты производительности и нагрузочные тесты
"""

import sys
import os
import time

sys.path.append(r'D:\_Work\my_projects\MathBot')

from math_solver import math_solver


def performance_test():
    """Тест производительности"""
    print("⚡ ТЕСТ ПРОИЗВОДИТЕЛЬНОСТИ")
    print("=" * 40)

    test_cases = [
        "2 + 2",
        "x + 5 = 10",
        "найти производную: x^2",
        "упростить (x + 1)^2",
        "cos(π/4)"
    ]

    times = []

    for problem in test_cases:
        start_time = time.time()
        result = math_solver.solve_problem(problem)
        end_time = time.time()

        processing_time = end_time - start_time
        times.append(processing_time)

        status = "✅" if result['success'] else "❌"
        print(f"{status} {problem:<30} {processing_time:.4f}с")

    avg_time = sum(times) / len(times)
    print(f"\n📊 Среднее время: {avg_time:.4f}с")
    print(f"🐌 Самое медленное: {max(times):.4f}с")
    print(f"🚀 Самое быстрое: {min(times):.4f}с")

    # Критерий производительности
    if avg_time < 0.1:
        print("🎉 Отличная производительность!")
    elif avg_time < 0.5:
        print("👍 Хорошая производительность")
    else:
        print("⚠️ Нужна оптимизация")


if __name__ == "__main__":
    performance_test()