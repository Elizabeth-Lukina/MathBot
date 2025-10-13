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

            # Извлекаем и нормализуем выражение
            expression_text = self._extract_expression(text)
            clean_text = self._normalize_expression(expression_text)
            
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
            return "simplify"  # по умолчанию упрощение

    def _extract_expression(self, text: str) -> str:
        """Извлекает математическое выражение из текста"""
        # Импортируем нормализатор
        from .expression_normalizer import expression_normalizer
        
        # Убираем русские команды
        clean_text = expression_normalizer._remove_russian_commands(text)
        
        # Ищем математическое выражение
        math_patterns = [
            r'([\(\)\w\s\+\-\*/\d\.\^]+)',  # общий паттерн
            r'\(([^)]+)\)',  # выражение в скобках
            r'(sin|cos|tan|cot|sec|csc)\([^)]+\)',  # тригонометрические функции
        ]
        
        for pattern in math_patterns:
            matches = re.findall(pattern, clean_text)
            if matches:
                # Берем самое длинное совпадение
                expression = max(matches, key=len).strip()
                if len(expression) > 2:  # минимальная длина выражения
                    return expression
        
        # Если не нашли, возвращаем очищенный текст
        return clean_text.strip()

    def _normalize_expression(self, text: str) -> str:
        """Нормализует математическое выражение"""
        if not text:
            return text
            
        # Импортируем нормализатор
        from .expression_normalizer import expression_normalizer
        
        # Используем общую нормализацию
        normalized = expression_normalizer.normalize_mathematical_text(text)
        
        # Дополнительная нормализация для тригонометрии
        normalized = self._fix_trigonometry_specific_issues(normalized)
        
        logger.info(f"Нормализованное выражение: {normalized}")
        return normalized

    def _fix_trigonometry_specific_issues(self, expression: str) -> str:
        """Исправляет проблемы специфичные для тригонометрии"""
        # Заменяем оставшиеся русские названия функций
        replacements = {
            'синус': 'sin', 'косинус': 'cos', 'тангенс': 'tan',
            'котангенс': 'cot', 'секанс': 'sec', 'косеканс': 'csc',
            'арксинус': 'asin', 'арккосинус': 'acos', 'арктангенс': 'atan'
        }
        
        normalized = expression
        for rus, eng in replacements.items():
            normalized = re.sub(rus, eng, normalized, flags=re.IGNORECASE)
        
        return normalized

    def _solve_computation(self, expr, original_text: str) -> Dict[str, Any]:
        """Решение вычислительных задач"""
        try:
            # Пробуем точное вычисление
            result = expr
            
            # Если выражение содержит pi, вычисляем численно
            if expr.has(pi):
                result = expr.evalf()
            else:
                # Пробуем упростить
                result = simplify(expr)
                
                # Если результат не константа, вычисляем численно
                if not result.is_constant():
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
        except Exception as e:
            logger.warning(f"Точное вычисление не удалось: {e}, пробуем численное")
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
            constant_value = simplified.evalf()
            steps.append(f"Результат: {constant_value}")
            explanation = f"Выражение равно {constant_value}"
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
        simplified = simplify(simplified)

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