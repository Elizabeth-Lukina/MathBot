#!/usr/bin/env python3
"""
Простой тест решателя
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import logging

logging.basicConfig(level=logging.INFO)

from math_solver import math_solver


def test_basic():
    """Базовый тест решателя"""
    print("🧪 Простой тест MathSolver")
    print("=" * 40)

    test_cases = [
        "2x + 3 = 7",
        "∫x^2 dx",
        "производная x^2",
        "sin(x) = 0.5",
        "2 + 2 * 2"
    ]

    for test in test_cases:
        print(f"\n🔹 {test}")
        result = math_solver.solve_with_steps(test)

        if result['success']:
            print(f"   ✅ {result['solution']}")
            print(f"   📊 Тип: {result['problem_type']}")
            print(f"   ⏱ Время: {result['processing_time']:.3f}с")
        else:
            print(f"   ❌ {result.get('error', 'Ошибка')}")


if __name__ == "__main__":
    test_basic()