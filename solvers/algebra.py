"""
Решатель алгебраических задач
"""

import sympy as sp
import logging
import re
from typing import Dict, Any
from sympy import symbols, parse_expr, simplify, expand, factor

logger = logging.getLogger(__name__)


class AlgebraSolver:
    """Решатель алгебраических задач"""

    def solve(self, text: str) -> Dict[str, Any]:
        """Решение алгебраических задач"""
        try:
            # Определяем операцию из текста
            operation = self._detect_operation(text)
            
            # Извлекаем выражение
            expression_text = self._extract_expression(text)
            
            # Нормализуем выражение
            clean_text = self._normalize_expression(expression_text)
            
            logger.info(f"Алгебра: операция='{operation}', выражение='{clean_text}'")

            # Парсим выражение
            expr = parse_expr(clean_text)

            # Выполняем нужную операцию
            if operation == 'expand':
                result = expand(expr)
                operation_name = 'раскрытие скобок'
                steps = [
                    f"Исходное выражение: {sp.latex(expr)}",
                    f"Операция: {operation_name}",
                    f"Результат: {sp.latex(result)}"
                ]
                
            elif operation == 'factor':
                result = factor(expr)
                operation_name = 'факторизация'
                steps = [
                    f"Исходное выражение: {sp.latex(expr)}",
                    f"Операция: {operation_name}",
                    f"Результат: {sp.latex(result)}"
                ]
                
            else:  # simplify
                # Для упрощения анализируем выражение и выбираем лучшую форму
                result, operation_name, steps = self._smart_simplify(expr)

            return {
                'success': True,
                'solution': str(result),
                'steps': steps,
                'latex': sp.latex(result),
                'explanation': f"Выполнено {operation_name} алгебраического выражения"
            }

        except Exception as e:
            logger.error(f"Ошибка алгебраических вычислений: {e}")
            return {
                'success': False,
                'solution': '',
                'steps': [],
                'latex': '',
                'explanation': f'Ошибка вычисления: {e}'
            }

    def _smart_simplify(self, expr):
        """Умное упрощение с выбором лучшей формы"""
        original_str = str(expr)
        
        # Пробуем разные формы
        simplified = simplify(expr)
        expanded = expand(expr)
        factored = factor(expr)
        
        # Определяем, какая форма лучше
        forms = [
            (simplified, 'упрощение', str(simplified)),
            (expanded, 'раскрытие скобок', str(expanded)),
            (factored, 'факторизация', str(factored))
        ]
        
        # Если исходное выражение содержит скобки в степени, предпочитаем раскрытие
        if any(char in original_str for char in ['(', ')']) and any(char in original_str for char in ['**', '^']):
            # Выражение со скобками в степени - раскрываем
            best_result = expanded
            best_operation = 'раскрытие скобок'
        else:
            # Выбираем самую короткую форму
            forms.sort(key=lambda x: len(x[2]))
            best_result = forms[0][0]
            best_operation = forms[0][1]
        
        steps = [
            f"Исходное выражение: {sp.latex(expr)}",
            f"Операция: {best_operation}",
            f"Результат: {sp.latex(best_result)}"
        ]
        
        return best_result, best_operation, steps

    def _detect_operation(self, text: str) -> str:
        """Определяет операцию из текста задачи"""
        text_lower = text.lower()

        if 'разложить' in text_lower or 'факторизац' in text_lower or 'множител' in text_lower:
            return 'factor'
        elif 'раскрыть' in text_lower or 'раскрой' in text_lower:
            return 'expand'
        elif 'упростить' in text_lower or 'упрощен' in text_lower:
            return 'simplify'
        else:
            # Анализируем выражение для автоматического определения
            if self._expression_has_powers(text):
                return 'expand'  # Выражения со степенями лучше раскрывать
            else:
                return 'simplify'

    def _expression_has_powers(self, text: str) -> bool:
        """Проверяет, содержит ли выражение степени"""
        power_patterns = [r'\*\*', r'\^', r'\(.*\)\s*[\*\^]']
        return any(re.search(pattern, text) for pattern in power_patterns)

    def _extract_expression(self, text: str) -> str:
        """Извлекает математическое выражение из текста"""
        # Убираем слова команд
        clean_text = re.sub(
            r'(упростить|разложить|раскрыть|решить|выражение|алгебраическое)\s*', 
            '', text, flags=re.IGNORECASE
        )
        
        # Ищем математическое выражение
        math_patterns = [
            r'([\(\)\w\s\+\-\*/\d\.\^]+)',  # общий паттерн
            r'\(([^)]+)\)',  # выражение в скобках
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
            
        # Заменяем ^ на **
        normalized = text.replace('^', '**')
        
        # Добавляем операторы умножения где нужно
        normalized = re.sub(r'(\d)([a-zA-Z\(])', r'\1*\2', normalized)  # 2x -> 2*x
        normalized = re.sub(r'([a-zA-Z\)])(\d|[a-zA-Z\(])', r'\1*\2', normalized)  # x2 -> x*2, xy -> x*y
        
        # Убираем лишние пробелы
        normalized = re.sub(r'\s+', '', normalized)
        
        logger.info(f"Нормализованное выражение: {normalized}")
        return normalized


# Глобальный экземпляр
algebra_solver = AlgebraSolver()
