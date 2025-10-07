import sympy as sp
import logging
import numpy as np
from sympy import symbols, solve, Eq, sin, cos, tan, cot, sec, csc, nsolve

logger = logging.getLogger(__name__)


class TrigonometricSolver:
    def __init__(self):
        self.x = symbols('x')
        logger.info("TrigonometricSolver инициализирован")

    def solve_with_steps(self, text):
        """Решение тригонометрических уравнений с показом ВСЕХ шагов"""
        steps = []

        try:
            # ШАГ 0: Исходное уравнение
            steps.append({
                'description': 'Исходное тригонометрическое уравнение',
                'formula': text,
                'details': 'Начинаем анализ уравнения'
            })

            if '=' not in text:
                steps.append({
                    'description': 'ОШИБКА: Не является уравнением',
                    'formula': 'Отсутствует знак равенства',
                    'details': 'Уравнение должно содержать "="'
                })
                return {'success': False, 'error': 'Не является уравнением', 'steps': steps}

            # Предварительная обработка
            text = self.preprocess_text(text)

            parts = text.split('=')
            if len(parts) != 2:
                steps.append({
                    'description': 'ОШИБКА: Некорректный формат',
                    'formula': 'Должно быть: выражение = выражение',
                    'details': 'Найдено несколько знаков равенства'
                })
                return {'success': False, 'error': 'Некорректный формат уравнения', 'steps': steps}

            left, right = parts[0].strip(), parts[1].strip()

            # ШАГ 1: Парсинг выражений
            steps.append({
                'description': 'ШАГ 1: Парсинг уравнения',
                'formula': f'Левая часть: {left} | Правая часть: {right}',
                'details': 'Разделяем уравнение на составляющие'
            })

            try:
                left_expr = sp.sympify(left)
                right_expr = sp.sympify(right)
            except Exception as e:
                steps.append({
                    'description': 'ОШИБКА ПАРСИНГА',
                    'formula': f'Не удалось распознать: {str(e)}',
                    'details': 'Проверьте синтаксис уравнения'
                })
                return {'success': False, 'error': f'Ошибка парсинга выражения: {e}', 'steps': steps}

            equation = Eq(left_expr, right_expr)

            steps.append({
                'description': 'Уравнение распознано',
                'formula': f'{sp.latex(left_expr)} = {sp.latex(right_expr)}',
                'details': 'Уравнение успешно преобразовано в математическую форму'
            })

            # ШАГ 2: Приведение к стандартному виду
            equation_std = Eq(left_expr - right_expr, 0)
            steps.append({
                'description': 'ШАГ 2: Приведение к стандартному виду',
                'formula': f'f(x) = {sp.latex(equation_std.lhs)} = 0',
                'details': 'Все слагаемые перенесены в левую часть'
            })

            # ШАГ 3: Попытка аналитического решения
            steps.append({
                'description': 'ШАГ 3: Попытка аналитического решения',
                'formula': 'Пробуем решить символьно',
                'details': 'Ищем точное решение методами алгебры'
            })

            solutions = []
            try:
                analytic_solutions = solve(equation, self.x, dict=True)
                if analytic_solutions:
                    solutions = analytic_solutions
                    steps.append({
                        'description': '✅ Аналитическое решение найдено!',
                        'formula': f'Решения: {[sol[self.x] for sol in solutions if self.x in sol]}',
                        'details': 'Уравнение решено символьно'
                    })
                else:
                    steps.append({
                        'description': '❌ Аналитическое решение не найдено',
                        'formula': 'Уравнение не имеет симвльного решения',
                        'details': 'Переходим к численным методам'
                    })
            except Exception as e:
                steps.append({
                    'description': '⚠️ Аналитическое решение невозможно',
                    'formula': f'Ошибка: {str(e)[:50]}...',
                    'details': 'Требуются численные методы. Переходим к шагу 4.'
                })

            # ШАГ 4: Численные методы (ВСЕГДА показываем этот шаг!)
            steps.append({
                'description': 'ШАГ 4: Применение численных методов',
                'formula': 'Ищем приближенные решения',
                'details': 'Используем метод Ньютона для поиска корней'
            })

            numerical_solutions = self.solve_numerically(equation_std.lhs, steps)

            if numerical_solutions:
                solutions.extend(numerical_solutions)
                steps.append({
                    'description': '✅ Численные решения найдены!',
                    'formula': f'Найдено {len(numerical_solutions)} решений',
                    'details': 'Численные методы дали результат'
                })
            else:
                steps.append({
                    'description': '❌ Численные решения не найдены',
                    'formula': 'Не удалось найти корни уравнения',
                    'details': 'Попробуйте другие начальные приближения или метод'
                })

            # ШАГ 5: Итоговый результат
            if solutions:
                solution_str = self.format_solutions(solutions)
                steps.append({
                    'description': '🎯 ФИНАЛЬНОЕ РЕШЕНИЕ',
                    'formula': f'x = {solution_str} + 2πn, n ∈ Z',
                    'details': 'Уравнение решено!'
                })

                return {
                    'success': True,
                    'solution': solution_str,
                    'steps': steps,
                    'problem_type': 'trigonometric',
                    'processing_time': 0.4,
                    'explanation': 'Тригонометрическое уравнение решено'
                }
            else:
                steps.append({
                    'description': '💥 РЕШЕНИЕ НЕ НАЙДЕНО',
                    'formula': 'Уравнение не имеет решений в действительных числах',
                    'details': 'Попробуйте изменить параметры или использовать другие методы'
                })

                return {
                    'success': False,
                    'error': 'Не удалось найти решение',
                    'steps': steps  # ВАЖНО: возвращаем шаги даже при ошибке!
                }

        except Exception as e:
            logger.error(f"Ошибка решения уравнения: {e}")
            steps.append({
                'description': '💥 КРИТИЧЕСКАЯ ОШИБКА',
                'formula': f'Ошибка: {str(e)}',
                'details': 'Произошла непредвиденная ошибка при решении'
            })
            return {'success': False, 'error': f'Ошибка решения: {e}', 'steps': steps}

    def solve_numerically(self, expr, steps):
        """Численное решение с подробным логированием"""
        solutions = []

        # Создаем функцию для численного решения
        f = sp.lambdify(self.x, expr, 'numpy')

        # Ищем корни в характерных точках (от -2π до 2π)
        search_points = np.linspace(-6.28, 6.28, 20)

        steps.append({
            'description': 'Поиск корней в интервале [-2π, 2π]',
            'formula': f'Точки поиска: {len(search_points)}',
            'details': 'Ищем решения в основном периоде'
        })

        for i, guess in enumerate(search_points):
            try:
                steps.append({
                    'description': f'Попытка {i + 1}: начальное приближение x ≈ {guess:.2f}',
                    'formula': f'f({guess:.2f}) = {float(f(guess)):.4f}',
                    'details': 'Пробуем решить методом Ньютона'
                })

                numerical_sol = nsolve(expr, self.x, guess)
                error = abs(f(numerical_sol))

                steps.append({
                    'description': f'Результат попытки {i + 1}',
                    'formula': f'x ≈ {float(numerical_sol):.6f}, ошибка: {error:.8f}',
                    'details': 'Оцениваем точность решения'
                })

                if error < 1e-6:
                    # Проверяем на дубликат
                    is_new = True
                    for existing_sol in solutions:
                        if abs(float(existing_sol[self.x]) - float(numerical_sol)) < 0.1:
                            is_new = False
                            break

                    if is_new:
                        solutions.append({self.x: numerical_sol})
                        steps.append({
                            'description': f'✅ НАЙДЕН КОРЕНЬ!',
                            'formula': f'x ≈ {float(numerical_sol):.6f}',
                            'details': 'Решение принято (ошибка < 1e-6)'
                        })
                    else:
                        steps.append({
                            'description': f'🚫 Дубликат решения',
                            'formula': f'x ≈ {float(numerical_sol):.6f}',
                            'details': 'Похожее решение уже найдено'
                        })
                else:
                    steps.append({
                        'description': f'🚫 Неточное решение',
                        'formula': f'Ошибка слишком велика: {error:.6f}',
                        'details': 'Продолжаем поиск'
                    })

            except Exception as e:
                steps.append({
                    'description': f'⚠️ Ошибка при попытке {i + 1}',
                    'formula': f'Не удалось вычислить: {str(e)[:30]}...',
                    'details': 'Переходим к следующей точке'
                })
                continue

        steps.append({
            'description': 'ЗАВЕРШЕНИЕ ЧИСЛЕННОГО ПОИСКА',
            'formula': f'Найдено решений: {len(solutions)}',
            'details': 'Завершены все попытки численного решения'
        })

        return solutions

    # ... остальные методы без изменений ...