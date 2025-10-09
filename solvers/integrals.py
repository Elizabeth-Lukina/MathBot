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
            r'from\s+[\d\.]+\s+to\s+[\d\.]+'
        ]
        return any(re.search(pattern, text, re.IGNORECASE) for pattern in patterns)

    def _solve_indefinite_integral(self, text: str) -> Dict[str, Any]:
        """Решение неопределенного интеграла"""
        try:
            # Нормализуем текст
            normalized_text = self._normalize_text(text)
            logger.info(f"Нормализовано: {normalized_text}")

            # Извлекаем части интеграла
            integrand, variable = self._extract_integral_parts(normalized_text)

            if not integrand:
                return self._error_response("Не удалось извлечь подынтегральное выражение")

            logger.info(f"Выражение: '{integrand}', переменная: '{variable}'")

            # ДОПОЛНИТЕЛЬНАЯ НОРМАЛИЗАЦИЯ выражения
            final_integrand = self._normalize_math_expression(integrand)
            logger.info(f"После мат. нормализации: '{final_integrand}'")

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
            # Нормализуем текст
            normalized_text = self._normalize_text(text)
            logger.info(f"Определенный интеграл: {normalized_text}")

            # ИЗВЛЕКАЕМ ПРЕДЕЛЫ - УЛУЧШЕННАЯ ВЕРСИЯ
            limits_match = re.search(r'от\s+([^\s]+)\s+до\s+([^\s]+)', normalized_text)
            if not limits_match:
                # Пробуем альтернативные форматы
                limits_match = re.search(r'∫.*?от\s+([^\s]+)\s+до\s+([^\s]+)', normalized_text)

            if not limits_match:
                return self._error_response("Не удалось извлечь пределы интегрирования")

            lower_limit_str = self._normalize_limit(limits_match.group(1))
            upper_limit_str = self._normalize_limit(limits_match.group(2))

            logger.info(f"Пределы: от {lower_limit_str} до {upper_limit_str}")

            # Парсим пределы
            lower_limit = parse_expr(lower_limit_str)
            upper_limit = parse_expr(upper_limit_str)

            # ИЗВЛЕКАЕМ ВЫРАЖЕНИЕ - УЛУЧШЕННАЯ ВЕРСИЯ
            # Убираем часть с пределами
            integrand_text = re.sub(r'от\s+[^\s]+\s+до\s+[^\s]+', '', normalized_text).strip()
            # Убираем ∫ если есть
            integrand_text = re.sub(r'^∫\s*', '', integrand_text).strip()
            # Убираем "dx" в конце если есть
            integrand_text = re.sub(r'\s*d[a-z]$', '', integrand_text).strip()

            # Если текст пустой, пробуем другой подход
            if not integrand_text:
                # Разделяем по "от"
                parts = normalized_text.split('от')
                if len(parts) > 0:
                    integrand_text = parts[0].replace('∫', '').strip()

            integrand, variable = self._extract_integral_parts(integrand_text)

            if not integrand:
                # Последняя попытка - берем все до "от"
                match = re.match(r'^(.*?)\s*от\s', normalized_text)
                if match:
                    integrand_text = match.group(1).replace('∫', '').strip()
                    integrand, variable = self._extract_integral_parts(integrand_text)

            if not integrand:
                return self._error_response("Не удалось извлечь подынтегральное выражение")

            logger.info(f"Выражение: '{integrand}', переменная: '{variable}'")

            # Дополнительная нормализация
            final_integrand = self._normalize_math_expression(integrand)
            logger.info(f"После мат. нормализации: '{final_integrand}'")

            # Парсим и вычисляем
            expr = parse_expr(final_integrand)
            var = symbols(variable)

            # ВЫЧИСЛЯЕМ определенный интеграл
            integral_result = integrate(expr, (var, lower_limit, upper_limit))

            # Если результат не вычислен численно, вычисляем его
            if integral_result.has(var):
                # Подставляем пределы
                upper_val = expr.subs(var, upper_limit)
                lower_val = expr.subs(var, lower_limit)
                integral_result = upper_val - lower_val

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

    def _normalize_text(self, text: str) -> str:
        """Нормализация текста"""
        # Заменяем π на pi
        normalized = text.replace('π', 'pi')

        # Заменяем ^ на **
        normalized = normalized.replace('^', '**')

        # Убираем лишние пробелы
        normalized = re.sub(r'\s+', ' ', normalized).strip()

        return normalized

    def _normalize_math_expression(self, expression: str) -> str:
        """НОРМАЛИЗАЦИЯ МАТЕМАТИЧЕСКОГО ВЫРАЖЕНИЯ - ИСПРАВЛЕННАЯ"""
        if not expression:
            return expression

        normalized = expression

        # 1. Заменяем 2x -> 2*x (но не sinx -> sin*x)
        normalized = re.sub(r'(\d)([a-zA-Z\(])', r'\1*\2', normalized)

        # 2. Заменяем x2 -> x*2
        normalized = re.sub(r'([a-zA-Z\)])(\d)', r'\1*\2', normalized)

        # 3. Заменяем )( -> )*(
        normalized = re.sub(r'(\))(\()', r'\1*\2', normalized)

        # 4. Обрабатываем e^x -> exp(x)
        normalized = re.sub(r'e\*\*\(([^)]+)\)', r'exp(\1)', normalized)
        normalized = re.sub(r'e\*\*([a-zA-Z])', r'exp(\1)', normalized)

        # 5. Заменяем ln на log
        normalized = re.sub(r'\bln\b', 'log', normalized)

        logger.info(f"Мат. нормализация: '{expression}' -> '{normalized}'")
        return normalized

    def _extract_integral_parts(self, text: str):
        """Извлекает подынтегральное выражение и переменную - ИСПРАВЛЕННАЯ"""
        if not text:
            return None, 'x'

        clean_text = re.sub(r'(интеграл|проинтегрировать|найти|вычислить|от)', '', text, flags=re.IGNORECASE)
        clean_text = clean_text.strip()

        # Убираем лишние слова в начале
        clean_text = re.sub(r'^(от|по)\s+', '', clean_text)

        # Паттерны в порядке приоритета
        patterns = [
            (r'∫\s*(.+?)\s*d([a-z])', 1, 2),  # ∫ выражение d переменная
            (r'(.+?)\s*d([xyz])', 1, 2),       # выражение d переменная
            (r'(.+?)\s*dx', 1, 'x'),           # выражение dx
        ]

        for pattern, integrand_group, var_group in patterns:
            match = re.search(pattern, clean_text)
            if match:
                integrand = match.group(integrand_group).strip()
                variable = match.group(var_group) if isinstance(var_group, str) else match.group(var_group)

                # Убираем возможные остатки
                integrand = re.sub(r'^\s*∫\s*', '', integrand)

                return integrand, variable

        # Если не нашли паттерн, берем весь текст как выражение
        # и пытаемся определить переменную
        if clean_text:
            # Ищем математические выражения (игнорируем отдельные буквы)
            math_pattern = r'([a-z]\([^)]+\)|[a-z]\*\*|\d+[a-z]|[a-z]+\d+|sin|cos|tan|log|exp|sqrt)'
            if re.search(math_pattern, clean_text):
                # Ищем переменные в выражении (игнорируем функции)
                variables = re.findall(r'\b([a-z])(?![a-z]*\()', clean_text)
                if variables:
                    variable = variables[0]  # берем первую найденную переменную
                else:
                    variable = 'x'

                return clean_text, variable
            else:
                # Если это просто одна функция типа "sin(x)", берем x как переменную
                return clean_text, 'x'

        return None, 'x'

    def _normalize_limit(self, limit_str: str) -> str:
        """Нормализует предел интегрирования"""
        normalized = limit_str.replace('π', 'pi')

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