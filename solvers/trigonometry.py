"""
Решатель тригонометрических задач
"""

import sympy as sp
import logging
import re
from typing import Dict, Any
from sympy import symbols, parse_expr, trigsimp, simplify, expand, sin, cos, tan, sec, csc, cot, pi, expand_trig

logger = logging.getLogger(__name__)


class TrigonometrySolver:
    """Решатель тригонометрических задач"""

    def solve(self, text: str) -> Dict[str, Any]:
        """Решение тригонометрических задач"""
        try:
            logger.info(f"Решаем тригонометрию: {text}")

            # Определяем тип задачи
            task_type = self._identify_task_type(text)
            logger.info(f"Тип задачи: {task_type}")

            # Очищаем и нормализуем текст
            clean_text = self._prepare_text(text)
            logger.info(f"Подготовленный текст: {clean_text}")

            # Парсим выражение
            expr = parse_expr(clean_text)

            # Обрабатываем в зависимости от типа задачи
            if task_type == "compute":
                return self._solve_computation(expr, clean_text)
            elif task_type == "simplify":
                return self._solve_simplification(expr, clean_text)
            elif task_type == "identity":
                return self._solve_identity(expr, clean_text)
            elif task_type == "derivative":
                return self._solve_derivative(expr, clean_text)
            elif task_type == "integral":
                return self._solve_integral(expr, clean_text)
            else:
                return self._solve_general(expr, clean_text)

        except Exception as e:
            logger.error(f"Ошибка решения тригонометрии: {e}")
            return {
                'success': False,
                'solution': '',
                'steps': [],
                'latex': '',
                'explanation': f'Ошибка решения: {e}'
            }

    def _identify_task_type(self, text: str) -> str:
        """Определяет тип тригонометрической задачи"""
        text_lower = text.lower()

        if any(word in text_lower for word in ['производная', 'дифференцировать']):
            return "derivative"
        elif any(word in text_lower for word in ['интеграл', 'проинтегрировать']):
            return "integral"
        elif any(word in text_lower for word in ['вычислить', 'найти значение', 'значение', '=']):
            return "compute"
        elif any(word in text_lower for word in ['упростить', 'упрощение']):
            return "simplify"
        elif any(word in text_lower for word in ['тождество', 'доказать']):
            return "identity"
        else:
            return "simplify"

    def _prepare_text(self, text: str) -> str:
        """Подготавливает текст для парсинга"""
        # Очищаем от русских слов
        clean_text = self._remove_task_words(text)

        # Нормализуем математические выражения
        normalized_text = self._normalize_mathematical_text(clean_text)

        return normalized_text

    def _remove_task_words(self, text: str) -> str:
        """Удаляет служебные слова из текста"""
        task_words = [
            'решить', 'найти', 'вычислить', 'синус', 'косинус', 'тангенс',
            'котангенс', 'тригонометрия', 'упростить', 'доказать', 'тождество',
            'значение', 'выражение'
        ]
        clean_text = text
        for word in task_words:
            clean_text = re.sub(word, '', clean_text, flags=re.IGNORECASE)
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        return clean_text

    def _normalize_mathematical_text(self, text: str) -> str:
        """Нормализация математического текста"""
        replacements = {
            'син': 'sin', 'кос': 'cos', 'тан': 'tan', 'тг': 'tan',
            'котан': 'cot', 'ктг': 'cot', 'пи': 'pi', '°': '',
            'градус': '', 'градусов': ''
        }

        text_normalized = text
        for russian, english in replacements.items():
            text_normalized = re.sub(russian, english, text_normalized, flags=re.IGNORECASE)

        text_normalized = text_normalized.replace('π', 'pi')
        text_normalized = text_normalized.replace('^', '**')

        # Заменяем градусы на радианы, если есть числовые значения с градусами
        degree_pattern = r'(\d+)\s*°'
        text_normalized = re.sub(degree_pattern, r'(\1*pi/180)', text_normalized)

        return text_normalized.strip()

    def _solve_computation(self, expr, original_text: str) -> Dict[str, Any]:
        """Решение вычислительных задач"""
        try:
            # Пробуем точное вычисление
            result = expr
            if expr.has(pi):
                result = expr.evalf()

            steps = [
                f"Исходное выражение: {sp.latex(expr)}",
                f"Результат: {sp.latex(result)}"
            ]

            return {
                'success': True,
                'solution': str(result),
                'steps': steps,
                'latex': sp.latex(expr) + f" = {sp.latex(result)}",
                'explanation': "Вычислено значение тригонометрического выражения"
            }
        except:
            # Если точное вычисление не удалось, используем численное
            result = expr.evalf()
            steps = [
                f"Исходное выражение: {sp.latex(expr)}",
                f"Численное значение: {result}"
            ]

            return {
                'success': True,
                'solution': str(result),
                'steps': steps,
                'latex': sp.latex(expr) + f" = {result}",
                'explanation': "Вычислено численное значение тригонометрического выражения"
            }

    def _solve_simplification(self, expr, original_text: str) -> Dict[str, Any]:
        """Упрощение тригонометрических выражений"""
        # Используем expand_trig для раскрытия тригонометрических выражений
        simplified = expand_trig(expr)

        # Дополнительно упрощаем
        simplified = trigsimp(simplified)
        simplified = simplify(simplified)

        steps = [
            f"Исходное выражение: {sp.latex(expr)}",
            f"Упрощенное выражение: {sp.latex(simplified)}"
        ]

        return {
            'success': True,
            'solution': str(simplified),
            'steps': steps,
            'latex': sp.latex(simplified),
            'explanation': "Упрощено тригонометрическое выражение"
        }

    def _solve_identity(self, expr, original_text: str) -> Dict[str, Any]:
        """Проверка тригонометрических тождеств"""
        simplified = simplify(expr)

        steps = [
            f"Исходное выражение: {sp.latex(expr)}",
            f"Упрощенное выражение: {sp.latex(simplified)}"
        ]

        # Проверяем, является ли выражение константой
        if simplified.is_constant():
            steps.append(f"Результат: {simplified}")
            explanation = f"Выражение равно {simplified}"
        else:
            explanation = "Выражение упрощено"

        return {
            'success': True,
            'solution': str(simplified),
            'steps': steps,
            'latex': sp.latex(simplified),
            'explanation': explanation
        }

    def _solve_derivative(self, expr, original_text: str) -> Dict[str, Any]:
        """Нахождение производных"""
        x = symbols('x')
        derivative = expr.diff(x)

        steps = [
            f"Функция: {sp.latex(expr)}",
            f"Производная: {sp.latex(derivative)}"
        ]

        return {
            'success': True,
            'solution': str(derivative),
            'steps': steps,
            'latex': sp.latex(derivative),
            'explanation': "Найдена производная функции"
        }

    def _solve_integral(self, expr, original_text: str) -> Dict[str, Any]:
        """Нахождение интегралов"""
        x = symbols('x')
        integral = sp.integrate(expr, x)

        steps = [
            f"Подынтегральное выражение: {sp.latex(expr)}",
            f"Интеграл: {sp.latex(integral)} + C"
        ]

        return {
            'success': True,
            'solution': str(integral) + " + C",
            'steps': steps,
            'latex': sp.latex(integral) + " + C",
            'explanation': "Найден неопределенный интеграл"
        }

    def _solve_general(self, expr, original_text: str) -> Dict[str, Any]:
        """Общее решение тригонометрических задач"""
        # Пробуем упростить
        simplified = expand_trig(expr)
        simplified = trigsimp(simplified)

        steps = [
            f"Исходное выражение: {sp.latex(expr)}",
            f"Результат: {sp.latex(simplified)}"
        ]

        return {
            'success': True,
            'solution': str(simplified),
            'steps': steps,
            'latex': sp.latex(simplified),
            'explanation': "Упрощено тригонометрическое выражение"
        }


# Глобальный экземпляр
trigonometry_solver = TrigonometrySolver()