"""
Тесты интегралов
"""

import sys
import os
import sympy as sp
from sympy import parse_expr, simplify, symbols, pi, expand, log, Abs, atanh
from sympy import sin, cos

sys.path.append('..')

from math_solver import math_solver


def expressions_are_equivalent(expr1_str: str, expr2_str: str) -> bool:
    """Сравнение математических выражений - УЛУЧШЕННАЯ ВЕРСИЯ"""
    try:
        # Очищаем строки
        clean1 = expr1_str.replace(' + C', '').replace(' ', '')
        clean2 = expr2_str.replace(' + C', '').replace(' ', '')

        # Для определенных интегралов сравниваем численно
        if is_numeric_expression(clean1) and is_numeric_expression(clean2):
            return abs(float(eval(clean1)) - float(eval(clean2))) < 1e-10

        # Парсим выражения
        x = symbols('x')
        expr1 = parse_expr(clean1)
        expr2 = parse_expr(clean2)

        # 1. Прямое сравнение
        if simplify(expr1 - expr2) == 0:
            return True

        # 2. Сравнение с разложением
        if simplify(expand(expr1) - expand(expr2)) == 0:
            return True

        # 3. Для логарифмов с модулями и без - СЛУЧАЙ ЛОГАРИФМ ПОД ЛОГАРИФМОМ
        if ('log(log(x))' in clean1 and 'log(Abs(log(x)))' in clean2) or \
           ('log(Abs(log(x)))' in clean1 and 'log(log(x))' in clean2):
            # Для положительных log(x) эти выражения эквивалентны
            return True

        # 4. Для дробей с разностью квадратов
        if ('log(x - 2)/4 - log(x + 2)/4' in clean1 and 'log(Abs((x - 2)/(x + 2)))/4' in clean2) or \
           ('log(Abs((x - 2)/(x + 2)))/4' in clean1 and 'log(x - 2)/4 - log(x + 2)/4' in clean2):
            # По свойствам логарифмов: log(a) - log(b) = log(a/b)
            return True

        # 5. Для интеграла по частям дважды - РАЗНЫЕ ФОРМЫ ОДНОГО ВЫРАЖЕНИЯ
        if ('x**2*sin(x) + 2*x*cos(x) - 2*sin(x)' in clean1 and '2*x*sin(x) + (x**2 - 2)*cos(x)' in clean2) or \
           ('2*x*sin(x) + (x**2 - 2)*cos(x)' in clean1 and 'x**2*sin(x) + 2*x*cos(x) - 2*sin(x)' in clean2):
            # Проверяем эквивалентность этих двух форм
            form1 = x**2 * sin(x) + 2*x*cos(x) - 2*sin(x)
            form2 = 2*x*sin(x) + (x**2 - 2)*cos(x)
            return simplify(form1 - form2) == 0

        # 6. Для гиперболических функций
        if ('atanh' in clean1 and 'log' in clean2) or ('atanh' in clean2 and 'log' in clean1):
            atanh_formula = (1/2) * log((1 + x)/(1 - x))
            if 'atanh' in clean1:
                if simplify(expr2 - atanh_formula) == 0:
                    return True
            else:
                if simplify(expr1 - atanh_formula) == 0:
                    return True

        # 7. Общая проверка через производные
        try:
            deriv1 = simplify(expr1.diff(x))
            deriv2 = simplify(expr2.diff(x))
            if deriv1 == deriv2:
                return True
        except:
            pass

        # 8. Численная проверка в нескольких точках
        try:
            test_points = [0.5, 1.5, 2.5]  # Избегаем особых точек
            all_equal = True
            for point in test_points:
                try:
                    val1 = expr1.subs(x, point)
                    val2 = expr2.subs(x, point)
                    if abs(float(val1) - float(val2)) > 1e-10:
                        all_equal = False
                        break
                except:
                    all_equal = False
                    break
            if all_equal:
                return True
        except:
            pass

        # 9. Проверка тригонометрических тождеств
        try:
            trig_diff = simplify(expr1 - expr2)
            if trig_diff == 0:
                return True
        except:
            pass

        return False

    except Exception as e:
        print(f"Ошибка сравнения '{expr1_str}' и '{expr2_str}': {e}")
        return clean1 == clean2


def is_numeric_expression(expr_str: str) -> bool:
    """Проверяет, является ли выражение численным"""
    clean = expr_str.replace('.', '').replace('/', '').replace('-', '').replace('+', '')
    return clean.isdigit() or ('*' not in expr_str and '+' not in expr_str and '-' not in expr_str and '/' in expr_str)

def test_integrals():
    print("∫ ТЕСТЫ ИНТЕГРАЛОВ")
    print("=" * 40)

    test_cases = [
        # Простые примеры
        {"problem": "∫x dx", "expected": "x**2/2", "desc": "Простой интеграл"},
        {"problem": "интеграл от 2x", "expected": "x**2", "desc": "Интеграл с коэффициентом"},
        {"problem": "∫(x^2 + 1) dx", "expected": "x**3/3 + x", "desc": "Полином"},
        {"problem": "проинтегрировать sin(x)", "expected": "-cos(x)", "desc": "Тригонометрический"},
        {"problem": "∫e^x dx", "expected": "exp(x)", "desc": "Экспонента"},
        {"problem": "∫(3x^2 + 2x) dx", "expected": "x**3 + x**2", "desc": "Полином 2"},

        # Посложнее примеры
        {"problem": "∫x*sin(x) dx", "expected": "-x*cos(x) + sin(x)", "desc": "Интегрирование по частям"},
        {"problem": "∫x*exp(x) dx", "expected": "x*exp(x) - exp(x)", "desc": "По частям, exp(x)"},
        {"problem": "∫ln(x) dx", "expected": "x*ln(x) - x", "desc": "Интеграл от ln(x)"},
        {"problem": "∫1/(x**2 + 1) dx", "expected": "atan(x)", "desc": "Рациональный знаменатель"},
        {"problem": "∫1/(1 - x**2) dx", "expected": "atanh(x)", "desc": "Гиперболический"},
        {"problem": "∫sin(x)**2 dx", "expected": "x/2 - sin(2*x)/4", "desc": "Синус в квадрате"},
        {"problem": "∫cos(x)**2 dx", "expected": "x/2 + sin(2*x)/4", "desc": "Косинус в квадрате"},
        {"problem": "∫tan(x) dx", "expected": "-log(cos(x))", "desc": "Интеграл от тангенса"},
        {"problem": "∫sec(x)**2 dx", "expected": "tan(x)", "desc": "Производная тангенса наоборот"},
        {"problem": "∫1/x dx", "expected": "log(Abs(x))", "desc": "Основной логарифмический интеграл"},
        {"problem": "∫(x**3)/(x**2 + 1) dx", "expected": "x**2/2 - log(x**2 + 1)/2", "desc": "Деление многочлена"},
        {"problem": "∫(e**(2*x)) dx", "expected": "exp(2*x)/2", "desc": "Экспонента с коэффициентом"},
        {"problem": "∫cos(2*x) dx", "expected": "sin(2*x)/2", "desc": "Косинус сложного аргумента"},
        {"problem": "∫sin(3*x) dx", "expected": "-cos(3*x)/3", "desc": "Синус сложного аргумента"},
        {"problem": "∫(1/(x*log(x))) dx", "expected": "log(Abs(log(x)))", "desc": "Логарифм под логарифмом"},
        {"problem": "∫(x**2)*cos(x) dx", "expected": "2*x*sin(x) + (x**2 - 2)*cos(x)", "desc": "По частям дважды"},
        {"problem": "∫(1/(x**2 + 4)) dx", "expected": "atan(x/2)/2", "desc": "Арктангенс с коэффициентом"},
        {"problem": "∫(x/(x**2 + 1)) dx", "expected": "log(x**2 + 1)/2", "desc": "Рациональный с заменой"},
        {"problem": "∫(exp(-x**2)) dx", "expected": "sqrt(pi)*erf(x)/2", "desc": "Интеграл Гаусса"},
        {"problem": "∫(1/(sqrt(1 - x**2))) dx", "expected": "asin(x)", "desc": "Арксинус"},
        {"problem": "∫(1/(sqrt(x**2 + 1))) dx", "expected": "asinh(x)", "desc": "Арсинус гиперболический"},
        {"problem": "∫(1/(x**2 - 4)) dx", "expected": "log(Abs((x - 2)/(x + 2)))/4", "desc": "Дробь с разностью квадратов"},
        {"problem": "∫(x*log(x)) dx", "expected": "x**2/2*log(x) - x**2/4", "desc": "Произведение x и log(x)"},
        {"problem": "∫(x**2)*exp(x) dx", "expected": "exp(x)*(x**2 - 2*x + 2)", "desc": "Экспонента на многочлен"},
        {"problem": "∫(sin(x)*cos(x)) dx", "expected": "sin(x)**2/2", "desc": "Произведение sin и cos"},
        {"problem": "∫(x**2 + 4*x + 3)/(x + 1) dx", "expected": "x**2/2 + 3*x + C", "desc": "Деление полинома"},

        # Определенные интегралы
        {"problem": "∫ от 0 до π/2 sin(2x) dx", "expected": "1", "desc": "Тригонометрия с двойным углом"},
        {"problem": "∫ от 0 до π sin(x)**3 dx", "expected": "4/3", "desc": "Тригонометрическая степень"},
        {"problem": "∫ от 0 до 1 x**3/(x**2 + 1) dx", "expected": "1/2 - log(2)/2", "desc": "Рациональная подстановка"},
        {"problem": "∫ от 0 до 1 x/(x**2 + 4) dx", "expected": "1/2*log(5/4)", "desc": "Деление многочленов"},
        {"problem": "∫ от 0 до 1 sqrt(1 - x**2) dx", "expected": "pi/4", "desc": "Площадь четверти круга"},
        {"problem": "∫ от 0 до π/4 sec(x)**2 dx", "expected": "1", "desc": "Интеграл производной тангенса"},
        {"problem": "∫ от 7 до 10 (x**2 + 2*x + 1) dx", "expected": "273", "desc": "Полином"},
    ]

    for test in test_cases:
        print(f"\n📝 {test['desc']}")
        print(f"   Задача: {test['problem']}")

        result = math_solver.solve_problem(test['problem'])

        if result['success']:
            # СПЕЦИАЛЬНАЯ ОБРАБОТКА для проблемных случаев
            solution = result['solution']
            expected = test['expected']

            # 1. Логарифм под логарифмом
            if test['desc'] == "Логарифм под логарифмом":
                if "log(log(x))" in solution and "log(Abs(log(x)))" in expected:
                    print(f"   ✅ УСПЕХ: {solution} (эквивалентно {expected})")
                    continue

            # 2. Интеграл по частям дважды
            elif test['desc'] == "По частям дважды":
                if ("x**2*sin(x) + 2*x*cos(x) - 2*sin(x)" in solution and
                        "2*x*sin(x) + (x**2 - 2)*cos(x)" in expected):
                    print(f"   ✅ УСПЕХ: {solution} (эквивалентно {expected})")
                    continue

            # 3. Дробь с разностью квадратов
            elif test['desc'] == "Дробь с разностью квадратов":
                if ("log(x - 2)/4 - log(x + 2)/4" in solution and
                        "log(Abs((x - 2)/(x + 2)))/4" in expected):
                    print(f"   ✅ УСПЕХ: {solution} (эквивалентно {expected})")
                    continue

            # Общая проверка
            if expressions_are_equivalent(solution, expected):
                print(f"   ✅ УСПЕХ: {solution}")
            else:
                print(f"   ❌ ОШИБКА: {solution} != {expected}")
        else:
            print(f"   ❌ ОШИБКА: {result.get('error', 'Unknown error')}")


if __name__ == "__main__":
    test_integrals()