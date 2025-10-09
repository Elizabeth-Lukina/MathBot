"""
Тесты тригонометрии
"""

import sys
import os
import sympy as sp
from sympy import symbols, simplify, expand, parse_expr, sin, cos, tan, sec, cot, pi, expand_trig

sys.path.append('..')

from math_solver import math_solver


def expressions_are_equivalent(expr1_str: str, expr2_str: str) -> bool:
    """Сравнение математических выражений для тригонометрии"""
    try:
        # Очищаем строки от пробелов, констант интегрирования и нормализуем формат
        clean1 = expr1_str.replace(' ', '').replace('^', '**').replace('+C', '')
        clean2 = expr2_str.replace(' ', '').replace('^', '**').replace('+C', '')

        # Для численных значений
        if is_numeric(clean1) and is_numeric(clean2):
            return abs(float(clean1) - float(clean2)) < 1e-10

        # Парсим выражения
        x = symbols('x')
        try:
            expr1 = parse_expr(clean1)
            expr2 = parse_expr(clean2)
        except:
            # Если парсинг не удался, сравниваем как строки
            return clean1 == clean2

        # Прямое сравнение
        if simplify(expr1 - expr2) == 0:
            return True

        # Сравнение с разложением тригонометрических выражений
        expr1_expanded = expand_trig(expr1)
        expr2_expanded = expand_trig(expr2)

        if simplify(expr1_expanded - expr2_expanded) == 0:
            return True

        # Для численных значений с плавающей точкой
        try:
            val1 = expr1.evalf()
            val2 = expr2.evalf()
            if abs(float(val1) - float(val2)) < 1e-10:
                return True
        except:
            pass

        return False

    except Exception as e:
        print(f"Ошибка сравнения '{expr1_str}' и '{expr2_str}': {e}")
        return clean1 == clean2


def is_numeric(s: str) -> bool:
    """Проверяет, является ли строка числом"""
    try:
        float(s)
        return True
    except:
        return False


def test_trigonometry():
    print("📊 ТЕСТЫ ТРИГОНОМЕТРИИ")
    print("=" * 40)

    test_cases = [
        # Базовые вычисления
        {"problem": "sin(0)", "expected": "0", "desc": "Синус 0"},
        {"problem": "cos(0)", "expected": "1", "desc": "Косинус 0"},
        {"problem": "sin(pi/2)", "expected": "1", "desc": "Синус pi/2"},
        {"problem": "cos(pi)", "expected": "-1", "desc": "Косинус pi"},
        {"problem": "tan(0)", "expected": "0", "desc": "Тангенс 0"},
        {"problem": "sin(pi/6)", "expected": "1/2", "desc": "Синус 30°"},
        {"problem": "cos(pi/3)", "expected": "1/2", "desc": "Косинус 60°"},

        # Основные тождества
        {"problem": "упростить sin(x)^2 + cos(x)^2", "expected": "1", "desc": "Тригонометрическое тождество"},
        {"problem": "упростить tan(x)/sec(x)", "expected": "sin(x)", "desc": "Выражение через синус"},
        {"problem": "упростить 1 + tan(x)^2", "expected": "sec(x)^2", "desc": "Основное тождество для тангенса"},
        {"problem": "упростить sin(x)/cos(x)", "expected": "tan(x)", "desc": "Определение тангенса"},
        {"problem": "упростить cos(x)/sin(x)", "expected": "cot(x)", "desc": "Определение котангенса"},

        # Формулы двойного угла
        {"problem": "упростить sin(2*x)", "expected": "2*sin(x)*cos(x)", "desc": "Формула двойного угла для синуса"},
        {"problem": "упростить cos(2*x)", "expected": "cos(x)^2 - sin(x)^2", "desc": "Формула двойного угла для косинуса"},
        {"problem": "упростить tan(2*x)", "expected": "2*tan(x)/(1 - tan(x)^2)", "desc": "Формула двойного угла для тангенса"},

        # Формулы сложения и вычитания
        {"problem": "упростить sin(pi/2 - x)", "expected": "cos(x)", "desc": "Формула дополнительного угла"},
        {"problem": "упростить cos(pi/2 - x)", "expected": "sin(x)", "desc": "Формула дополнительного угла"},
        {"problem": "упростить sin(x + pi)", "expected": "-sin(x)", "desc": "Сдвиг на π"},
        {"problem": "упростить cos(x + pi)", "expected": "-cos(x)", "desc": "Сдвиг на π"},

        # Формулы понижения степени
        {"problem": "упростить (1 - cos(2*x))/2", "expected": "sin(x)^2", "desc": "Формула понижения степени для синуса"},
        {"problem": "упростить (1 + cos(2*x))/2", "expected": "cos(x)^2", "desc": "Формула понижения степени для косинуса"},
        {"problem": "упростить sin(x)*cos(x)", "expected": "sin(2*x)/2", "desc": "Обратная формула двойного угла"},

        # Дополнительные тесты
        {"problem": "упростить sin(x)^4 + 2*sin(x)^2*cos(x)^2 + cos(x)^4", "expected": "1", "desc": "Квадрат суммы тождества"},
        {"problem": "упростить sin(3*x)", "expected": "3*sin(x) - 4*sin(x)^3", "desc": "Формула тройного угла"},
        {"problem": "упростить cos(3*x)", "expected": "4*cos(x)^3 - 3*cos(x)", "desc": "Формула тройного угла"},
        {"problem": "упростить sin(x) + sin(3*x)", "expected": "2*sin(2*x)*cos(x)", "desc": "Сумма синусов"},
        {"problem": "упростить cos(x) + cos(3*x)", "expected": "2*cos(2*x)*cos(x)", "desc": "Сумма косинусов"},
        {"problem": "упростить sin(x) - sin(3*x)", "expected": "-2*cos(2*x)*sin(x)", "desc": "Разность синусов"},
        {"problem": "упростить cos(x) - cos(3*x)", "expected": "2*sin(2*x)*sin(x)", "desc": "Разность косинусов"}
    ]

    passed = 0
    failed = 0

    for test in test_cases:
        print(f"\n📝 {test['desc']}")
        print(f"   Задача: {test['problem']}")

        result = math_solver.solve_problem(test['problem'])

        if result['success']:
            if expressions_are_equivalent(result['solution'], test['expected']):
                print(f"   ✅ УСПЕХ: {result['solution']}")
                passed += 1
            else:
                print(f"   ❌ ОШИБКА: {result['solution']} != {test['expected']}")
                failed += 1
        else:
            print(f"   ❌ ОШИБКА: {result.get('error', 'Unknown error')}")
            failed += 1

    print(f"\n{'='*40}")
    print(f"📈 ИТОГ: {passed} прошло, {failed} не прошло")
    print(f"{'='*40}")


if __name__ == "__main__":
    test_trigonometry()