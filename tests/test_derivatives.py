"""
Тесты производных
"""

import sys
import os
import sympy as sp
from sympy import parse_expr, simplify

sys.path.append('..')

from math_solver import math_solver


def test_derivatives():
    print("📈 ТЕСТЫ ПРОИЗВОДНЫХ")
    print("=" * 40)

    test_cases = [
        {"problem": "найти производную: x^2", "expected": "2*x", "desc": "Простая производная"},
        {"problem": "производная от 3x^2 + 2x + 1", "expected": "6*x + 2", "desc": "Полином"},
        {"problem": "f(x) = x^3 - 2x", "expected": "3*x**2 - 2", "desc": "Функция f(x)"},
        {"problem": "дифференцировать sin(x)", "expected": "cos(x)", "desc": "Тригонометрическая функция"},
        {"problem": "производная e^x", "expected": "exp(x)", "desc": "Экспонента"},
        {"problem": "найти f'(x) для x^4", "expected": "4*x**3", "desc": "Степень 4"},
        {"problem": "производная cos(x)", "expected": "-sin(x)", "desc": "Косинус"},
        {"problem": "f(x) = ln(x)", "expected": "1/x", "desc": "Логарифм"},
        # --- Сложные тесты ---
        {"problem": "f(x) = x^2 * sin(x)", "expected": "2*x*sin(x) + x**2*cos(x)", "desc": "Производная произведения"},
        {"problem": "f(x) = sin(x)/x", "expected": "(x*cos(x) - sin(x))/x**2", "desc": "Производная частного"},
        {"problem": "f(x) = e^(2x)", "expected": "2*exp(2*x)", "desc": "Экспонента с внутренней функцией"},
        {"problem": "f(x) = ln(sin(x))", "expected": "cos(x)/sin(x)", "desc": "Составная функция логарифма"},
        {"problem": "f(x) = sin(x^2)", "expected": "2*x*cos(x**2)", "desc": "Сложная функция sin(x²)"},
        {"problem": "f(x) = cos(3x)", "expected": "-3*sin(3*x)", "desc": "Косинус сложного аргумента"},
        {"problem": "f(x) = tan(x)", "expected": "1/cos(x)**2", "desc": "Тангенс"},
        {"problem": "f(x) = x^2 * e^x", "expected": "2*x*exp(x) + x**2*exp(x)",
         "desc": "Произведение степенной и экспоненты"},
        {"problem": "f(x) = e^(sin(x))", "expected": "cos(x)*exp(sin(x))", "desc": "Экспонента от синуса"},
        {"problem": "f(x) = ln(x^2 + 1)", "expected": "2*x/(x**2 + 1)", "desc": "Логарифм сложного аргумента"},
        {"problem": "f(x) = sqrt(x)", "expected": "1/(2*sqrt(x))", "desc": "Корень квадратный"},
        {"problem": "f(x) = 1/x^2", "expected": "-2/x**3", "desc": "Обратная степень"},
        {"problem": "f(x) = (x^2 + 1)*(x - 3)", "expected": "2*x*(x - 3) + (x**2 + 1)",
         "desc": "Произведение полиномов"},
        {"problem": "f(x) = (x^3 + 2x)/(x^2 + 1)",
         "expected": "((3*x**2 + 2)*(x**2 + 1) - (x**3 + 2*x)*2*x)/(x**2 + 1)**2", "desc": "Сложная дробь"},
        {"problem": "f(x) = sin(x)*cos(x)", "expected": "cos(x)**2 - sin(x)**2", "desc": "Производная sin(x)*cos(x)"},
        {"problem": "f(x) = arctan(x)", "expected": "1/(1 + x**2)", "desc": "Арктангенс"},
        {"problem": "f(x) = x*sin(x^2)", "expected": "sin(x**2) + 2*x**2*cos(x**2)",
         "desc": "Произведение с внутренней функцией"},
        {"problem": "f(x) = e^(x^2 + 1)", "expected": "2*x*exp(x**2 + 1)", "desc": "Экспонента от полинома"},
        {"problem": "f(x) = ln(cos(x))", "expected": "-sin(x)/cos(x)", "desc": "Логарифм косинуса"},
        {"problem": "f(x) = x / (1 + x^2)", "expected": "(1 - x**2)/(1 + x**2)**2", "desc": "Рациональная функция"}
    ]

    for test in test_cases:
        print(f"\n📝 {test['desc']}")
        print(f"   Задача: {test['problem']}")

        result = math_solver.solve_problem(test['problem'])

        if result['success']:
            # Сравниваем математические выражения, а не строки
            try:
                # Парсим ожидаемое и полученное выражения
                expected_expr = parse_expr(test['expected'])
                solution_expr = parse_expr(str(result['solution']))

                # Упрощаем разность - если 0, то выражения равны
                difference = simplify(expected_expr - solution_expr)

                if difference == 0:
                    print(f"   ✅ УСПЕХ: {result['solution']}")
                else:
                    print(f"   ❌ ОШИБКА: {result['solution']} != {test['expected']}")
                    print(f"       Разность: {difference}")

            except Exception as e:
                # Если не удалось распарсить, сравниваем как строки
                if test['expected'] in str(result['solution']):
                    print(f"   ✅ УСПЕХ: {result['solution']}")
                else:
                    print(f"   ❌ ОШИБКА: {result['solution']} != {test['expected']}")
                    print(f"       Ошибка сравнения: {e}")
        else:
            print(f"   ❌ ОШИБКА: {result.get('error', 'Unknown error')}")


if __name__ == "__main__":
    test_derivatives()