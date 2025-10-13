"""
Решатель интегралов
"""

import sympy as sp
import logging
import re
from typing import Dict, Any
from sympy import symbols, integrate, parse_expr, simplify, pi, log, Abs, atanh, expand, sin, cos, tan, sec, sqrt, exp, asin, asinh, atan, erf

logger = logging.getLogger(__name__)


class IntegralSolver:
    """Решатель интегралов"""

    def solve(self, text: str) -> Dict[str, Any]:
        """Решение интегралов"""
        try:
            logger.info(f"=== ИНТЕГРАЛ: {text} ===")

            # Определяем тип интеграла
            if self._is_definite_integral(text):
                return self._solve_definite_integral(text)
            else:
                return self._solve_indefinite_integral(text)

        except Exception as e:
            logger.error(f"Ошибка вычисления интеграла: {e}")
            return {
                'success': False,
                'solution': '',
                'steps': [],
                'latex': '',
                'explanation': f'Ошибка вычисления интеграла: {e}'
            }

    def _is_definite_integral(self, text: str) -> bool:
        """Проверяет, является ли интеграл определенным"""
        patterns = [
            r'от\s+[\d\.π/]+\s+до\s+[\d\.π/]+',
            r'∫.*?[\(\[]\s*[\d\.]+\s*,\s*[\d\.]+\s*[\)\]]',
            r'from\s+[\d\.]+\s+to\s+[\d\.]+',
            r'предел.*?от.*?до'
        ]
        return any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns)

    def _solve_indefinite_integral(self, text: str) -> Dict[str, Any]:
        """Решение неопределенного интеграла"""
        try:
            logger.info(f"Неопределенный интеграл: {text}")

            # Извлекаем части интеграла
            integrand, variable = self._extract_integral_parts(text)

            if not integrand:
                return self._error_response("Не удалось извлечь подынтегральное выражение")

            logger.info(f"Выражение: '{integrand}', переменная: '{variable}'")

            # Нормализуем выражение
            final_integrand = self._normalize_integrand(integrand)
            logger.info(f"После нормализации: '{final_integrand}'")

            # Парсим выражение
            expr = parse_expr(final_integrand)
            var = symbols(variable)

            # Вычисляем интеграл
            integral_result = integrate(expr, var)

            # Упрощаем результат
            final_result = simplify(integral_result)

            steps = [
                f"Подынтегральное выражение: {sp.latex(expr)}",
                f"Переменная интегрирования: {variable}",
                f"Интеграл: ∫{sp.latex(expr)} d{variable}",
                f"Результат: {sp.latex(final_result)} + C"
            ]

            return {
                'success': True,
                'solution': str(final_result) + ' + C',
                'steps': steps,
                'latex': sp.latex(final_result) + ' + C',
                'explanation': "Вычислен неопределенный интеграл"
            }

        except Exception as e:
            logger.error(f"Ошибка неопределенного интеграла: {e}")
            return self._error_response(f'Ошибка вычисления: {e}')

    def _solve_definite_integral(self, text: str) -> Dict[str, Any]:
        """Решение определенного интеграла"""
        try:
            logger.info(f"Определенный интеграл: {text}")

            # ИЗВЛЕКАЕМ ПРЕДЕЛЫ
            limits_match = re.search(r'от\s+([^\s]+)\s+до\s+([^\s]+)', text)
            if not limits_match:
                # Пробуем альтернативные форматы
                limits_match = re.search(r'∫.*?от\s+([^\s]+)\s+до\s+([^\s]+)', text)
                if not limits_match:
                    limits_match = re.search(r'предел.*?от\s+([^\s]+)\s+до\s+([^\s]+)', text, re.IGNORECASE)

            if not limits_match:
                return self._error_response("Не удалось извлечь пределы интегрирования")

            lower_limit_str = self._normalize_limit(limits_match.group(1))
            upper_limit_str = self._normalize_limit(limits_match.group(2))

            logger.info(f"Пределы: от {lower_limit_str} до {upper_limit_str}")

            # Парсим пределы
            lower_limit = parse_expr(lower_limit_str)
            upper_limit = parse_expr(upper_limit_str)

            # ИЗВЛЕКАЕМ ВЫРАЖЕНИЕ
            integrand_text = self._extract_integrand_from_text(text)
            
            integrand, variable = self._extract_integral_parts(integrand_text)

            if not integrand:
                return self._error_response("Не удалось извлечь подынтегральное выражение")

            logger.info(f"Выражение: '{integrand}', переменная: '{variable}'")

            # Нормализуем выражение
            final_integrand = self._normalize_integrand(integrand)
            logger.info(f"После нормализации: '{final_integrand}'")

            # Парсим и вычисляем
            expr = parse_expr(final_integrand)
            var = symbols(variable)

            # ВЫЧИСЛЯЕМ определенный интеграл
            integral_result = integrate(expr, (var, lower_limit, upper_limit))

            # Если результат содержит переменную, вычисляем численно
            if integral_result.has(var):
                try:
                    # Пробуем вычислить численно
                    integral_result = integral_result.evalf()
                except:
                    # Если не получается, оставляем как есть
                    pass

            # Упрощаем результат
            final_result = simplify(integral_result)

            steps = [
                f"Подынтегральное выражение: {sp.latex(expr)}",
                f"Переменная интегрирования: {variable}",
                f"Пределы: от {sp.latex(lower_limit)} до {sp.latex(upper_limit)}",
                f"Интеграл: ∫_{{{sp.latex(lower_limit)}}}^{{{sp.latex(upper_limit)}}} {sp.latex(expr)} d{variable}",
                f"Результат: {sp.latex(final_result)}"
            ]

            return {
                'success': True,
                'solution': str(final_result),
                'steps': steps,
                'latex': sp.latex(final_result),
                'explanation': "Вычислен определенный интеграл"
            }

        except Exception as e:
            logger.error(f"Ошибка определенного интеграла: {e}")
            return self._error_response(f'Ошибка вычисления: {e}')

    def _extract_integrand_from_text(self, text: str) -> str:
        """Извлекает подынтегральное выражение из текста"""
        # Сначала убираем часть с пределами
        integrand_text = re.sub(r'от\s+[^\s]+\s+до\s+[^\s]+', '', text).strip()
        
        # Убираем ∫ если есть
        integrand_text = re.sub(r'^∫\s*', '', integrand_text).strip()
        
        # Убираем "dx", "dy" и т.д. в конце если есть
        integrand_text = re.sub(r'\s*d[a-z]\s*$', '', integrand_text).strip()

        # Если текст пустой, пробуем другой подход
        if not integrand_text:
            # Разделяем по "от"
            parts = text.split('от')
            if len(parts) > 0:
                integrand_text = parts[0].replace('∫', '').strip()

        # Если все еще пусто, берем все до первого "от"
        if not integrand_text:
            match = re.match(r'^(.*?)\s*от\s', text)
            if match:
                integrand_text = match.group(1).replace('∫', '').strip()

        return integrand_text

    def _extract_integral_parts(self, text: str):
        """Извлекает подынтегральное выражение и переменную - УЛУЧШЕННАЯ ВЕРСИЯ"""
        if not text:
            return None, 'x'

        # Очищаем текст от русских команд интегралов
        clean_text = self._clean_integral_text(text)
        logger.info(f"Очищенный текст: '{clean_text}'")

        # Паттерны в порядке приоритета
        patterns = [
            (r'∫\s*(.+?)\s*d([a-z])', 1, 2),  # ∫ выражение d переменная
            (r'(.+?)\s*d([a-z])', 1, 2),       # выражение d переменная
            (r'(.+?)\s*dx', 1, 'x'),           # выражение dx
            (r'(.+?)\s*dy', 1, 'y'),           # выражение dy
            (r'(.+?)\s*dt', 1, 't'),           # выражение dt
        ]

        for pattern, integrand_group, var_group in patterns:
            match = re.search(pattern, clean_text, re.IGNORECASE)
            if match:
                integrand = match.group(integrand_group).strip()
                variable = match.group(var_group) if isinstance(var_group, str) else match.group(var_group)

                # Убираем возможные остатки
                integrand = re.sub(r'^\s*∫\s*', '', integrand)

                logger.info(f"Найдено по паттерну: '{integrand}', '{variable}'")
                return integrand, variable

        # Если не нашли паттерн, ищем математическое выражение
        math_expression = self._extract_math_expression(clean_text)
        if math_expression:
            # Определяем переменную по содержимому выражения
            variable = self._detect_variable(math_expression)
            logger.info(f"Найдено математическое выражение: '{math_expression}', '{variable}'")
            return math_expression, variable

        return None, 'x'

    def _clean_integral_text(self, text: str) -> str:
        """Очищает текст от русских команд интегралов"""
        # Убираем русские команды интегралов
        integral_commands = [
            'интеграл', 'проинтегрировать', 'найти', 'вычислить', 
            'решить', 'взять', 'посчитать'
        ]
        
        clean_text = text
        for command in integral_commands:
            clean_text = re.sub(command, '', clean_text, flags=re.IGNORECASE)
        
        # Убираем лишние пробелы
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        
        # Убираем "от" в начале
        clean_text = re.sub(r'^\s*от\s+', '', clean_text)
        
        return clean_text

    def _extract_math_expression(self, text: str) -> str:
        """Извлекает математическое выражение из текста"""
        # Паттерны для математических выражений
        math_patterns = [
            r'([a-zA-Z\d+\-*/\^\.\s\(\)eπ]+)',  # общий математический паттерн
            r'(sin|cos|tan|log|exp|sqrt)\([^)]+\)',  # функции
            r'(\d+[a-zA-Z]|[a-zA-Z]\d+)',  # 2x, x2 и т.д.
        ]
        
        for pattern in math_patterns:
            matches = re.findall(pattern, text)
            if matches:
                # Берем самое длинное совпадение
                expression = max(matches, key=len).strip()
                if len(expression) >= 2:  # минимальная длина выражения
                    return expression
        
        return None

    def _detect_variable(self, expression: str) -> str:
        """Определяет переменную интегрирования"""
        # Ищем буквенные переменные (игнорируя функции)
        variables = re.findall(r'\b([a-z])(?![a-z]*\()', expression, re.IGNORECASE)
        
        if variables:
            # Предпочитаем x, затем y, затем t, затем первую найденную
            preferred_vars = ['x', 'y', 't', 'z']
            for var in preferred_vars:
                if var in variables:
                    return var
            return variables[0]
        
        # Если не нашли, используем x по умолчанию
        return 'x'

    def _normalize_integrand(self, integrand: str) -> str:
        """Нормализует подынтегральное выражение"""
        if not integrand:
            return integrand

        # Импортируем нормализатор для базовой нормализации
        from .expression_normalizer import expression_normalizer
        
        # Базовая нормализация
        normalized = expression_normalizer.normalize_expression(integrand)
        
        # Дополнительная нормализация специфичная для интегралов
        normalized = self._fix_integral_specific_issues(normalized)
        
        return normalized

    def _fix_integral_specific_issues(self, expression: str) -> str:
        """Исправляет проблемы специфичные для интегралов"""
        # Заменяем оставшиеся русские слова
        replacements = {
            'син': 'sin', 'кос': 'cos', 'тан': 'tan',
            'пи': 'pi', 'е': 'e'
        }
        
        normalized = expression
        for rus, eng in replacements.items():
            normalized = re.sub(rus, eng, normalized, flags=re.IGNORECASE)
        
        return normalized

    def _normalize_limit(self, limit_str: str) -> str:
        """Нормализует предел интегрирования"""
        normalized = limit_str.replace('π', 'pi')
        normalized = normalized.replace('^', '**')

        if '/' in normalized and not re.search(r'[a-zA-Z]', normalized):
            parts = normalized.split('/')
            if len(parts) == 2:
                return f"({parts[0]})/({parts[1]})"

        return normalized

    def _error_response(self, message: str) -> Dict[str, Any]:
        """Создает ответ с ошибкой"""
        return {
            'success': False,
            'solution': '',
            'steps': [],
            'latex': '',
            'explanation': message
        }


# Глобальный экземпляр
integral_solver = IntegralSolver()