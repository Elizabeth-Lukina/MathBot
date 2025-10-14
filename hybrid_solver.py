"""
Гибридный решатель - объединяет точность SymPy и AI объяснения
"""

import logging
import time
import json
import re
import requests
from typing import Dict, Any
from math_solver import math_solver
from config import SOLUTION_MODES, OPENAI_API_KEY

logger = logging.getLogger(__name__)


class HybridSolver:
    """Гибридный решатель с AI объяснениями"""

    def __init__(self):
        self.sympy_solver = math_solver

    def solve_with_mode(self, problem_text: str, mode: str = 'exam') -> Dict[str, Any]:
        """Решает задачу с AI объяснениями"""
        print(f"🔍 hybrid_solver: режим {mode}, задача: {problem_text}")  # ОТЛАДКА

        # 1. Решаем через SymPy
        sympy_result = self.sympy_solver.solve_problem(problem_text)

        if not sympy_result['success']:
            return sympy_result

        # 2. Для быстрого режима - только ответ
        if mode == 'quick':
            print("🔍 hybrid_solver: быстрый режим - только ответ")  # ОТЛАДКА
            return {
                'success': True,
                'solution': sympy_result['solution'],
                'explanation': f"Ответ: {sympy_result['solution']}",
                'problem_type': sympy_result['problem_type']
            }

        # 3. Для exam и tutor режимов - ГЕНЕРИРУЕМ AI ОБЪЯСНЕНИЕ
        print(f"🔍 hybrid_solver: генерируем AI объяснение для режима {mode}")  # ОТЛАДКА

        ai_explanation = self._generate_ai_explanation(
            problem_text,
            sympy_result,
            mode
        )

        print(f"🔍 hybrid_solver: результат AI: {ai_explanation}")  # ОТЛАДКА

        if ai_explanation['success']:
            # Возвращаем AI объяснение
            return {
                'success': True,
                'solution': sympy_result['solution'],
                'explanation': ai_explanation['explanation'],
                'problem_type': sympy_result['problem_type'],
                'source': 'ai'
            }
        else:
            # Fallback на SymPy объяснение
            print(f"🔍 hybrid_solver: AI не сработал, используем fallback")  # ОТЛАДКА
            return {
                'success': True,
                'solution': sympy_result['solution'],
                'explanation': f"Задача: {problem_text}\n\nОтвет: {sympy_result['solution']}",
                'problem_type': sympy_result['problem_type'],
                'source': 'sympy',
                'ai_error': ai_explanation.get('error')
            }

    def _generate_ai_explanation(self, problem_text: str, sympy_result: Dict, mode: str) -> Dict[str, Any]:
        """Генерирует AI объяснение через proxyapi.ru"""
        try:
            # Подготавливаем промпт в зависимости от режима
            prompt = self._create_prompt(problem_text, sympy_result, mode)

            # Отправляем запрос к AI
            response_text = self._call_proxyapi(prompt)

            if not response_text:
                return {'success': False, 'error': 'AI сервис недоступен'}

            # Парсим и валидируем ответ AI
            return self._parse_ai_response(response_text, sympy_result['solution'])

        except Exception as e:
            logger.error(f"Ошибка генерации AI объяснения: {e}")
            return {'success': False, 'error': str(e)}

    def _create_prompt(self, problem_text: str, sympy_result: Dict, mode: str) -> str:
        """Создает промпт для AI"""

        if mode == 'quick':
            return ""

        base_instructions = f"""
    Ты - универсальный математический эксперт. Реши задачу и предоставь ответ в формате JSON.
    Задача: {problem_text}
    Уже вычисленное решение SymPy: {sympy_result['solution']}
    Тип задачи: {sympy_result.get('problem_type', 'unknown')}
    """

        if mode == 'exam':
            format_instructions = """
    Верни ответ в формате JSON:
    {
    "solution": "{solution}",
    "steps": ["четкий шаг 1", "четкий шаг 2", "четкий шаг 3"],
    "explanation": "краткое и понятное объяснение решения"
    }

    Требования для exam режима: СУХО
    - Шаги должны быть четкими и последовательными
    - Объяснение должно быть лаконичным(без лишней теории)
    - Акцент на логике решения
    """
        else:  # tutor режим
            format_instructions = """
    Верни ответ в формате JSON:
    { 
    "solution": "{solution}",
    "steps": ["подробный шаг 1 с пояснениями", "подробный шаг 2 с пояснениями", "подробный шаг 3 с пояснениями"],
    "explanation": "развернутое объяснение метода решения",
    "theory": "теоретическая база: какие правила, формулы и теоремы применяются",
    "tips": ["практический совет 1", "практический совет 2"],
    "common_mistakes": ["распространенная ошибка 1", "распространенная ошибка 2"]
    }

    Требования для tutor режима:
    - Если пример достаточно простой, то лишнего не пиши, исходя из сложности задания
    - Будь максимально подробным в объяснениях
    - Объясни КАК и ПОЧЕМУ работает каждый метод
    - Дай практические советы для подобных задач
    - Предупреди о типичных ошибках
    - Объясни теоретическую основу
    """

        # Универсальные советы для всех типов задач
        universal_advice = """
    Универсальные рекомендации:
    - Анализируй тип задачи и выбирай соответствующий метод
    - Объясни почему выбран именно этот метод решения
    - Покажи применение математических правил и формул
    - Для производных: объясни правила дифференцирования
    - Для интегралов: объясни методы интегрирования  
    - Для уравнений: объясни методы решения
    - Для пределов: объясни правила вычисления
    - Убедись, что объяснение понятно студенту
    """

        critical_instructions = f"""
    КРИТИЧЕСКИ ВАЖНО:
    1. Поле "solution" должно быть точно: {sympy_result['solution']}
    2. Не меняй математическое выражение в solution
    3. Используй обычный текст (без Markdown: *, _, `)
    4. JSON должен быть валидным (проверь запятые)
    5. Для tutor режима заполни ВСЕ поля подробно
    6. Адаптируй объяснение под тип задачи
    Начни анализ с определения типа задачи и выбора метода решения.
    """

        prompt = base_instructions + format_instructions.format(
            solution=sympy_result['solution']) + universal_advice + critical_instructions

        return prompt

    def _call_proxyapi(self, prompt: str) -> str:
        """Вызывает proxyapi.ru с улучшенным системным промптом"""
        try:
            url = "https://api.proxyapi.ru/openai/v1/chat/completions"

            headers = {
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "Content-Type": "application/json"
            }

            data = {
                "model": "gpt-3.5-turbo",
                "messages": [
                    {
                        "role": "system",
                        "content": """Ты универсальный математический эксперт. 
    Твоя задача - решать ЛЮБЫЕ типы математических задач: производные, интегралы, уравнения, пределы, матрицы и т.д.
    Всегда отвечай в формате JSON. Убедись, что JSON валидный.
    Адаптируй объяснение под тип задачи.
    Будь точным в математических выражениях."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.3,
                "max_tokens": 2000
            }

            response = requests.post(
                url,
                headers=headers,
                json=data,
                timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                logger.error(f"Ошибка ProxyAPI: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            logger.error(f"Ошибка вызова ProxyAPI: {e}")
            return None

    def _parse_ai_response(self, response_text: str, expected_solution: str) -> Dict[str, Any]:
        """Парсит и валидирует ответ AI"""
        try:
            print(f"🔍 RAW AI RESPONSE: {response_text}")  # ДЛЯ ОТЛАДКИ

            # Чистим ответ от возможных лишних символов
            cleaned_response = self._clean_json_response(response_text)

            print(f"🔍 CLEANED AI RESPONSE: {cleaned_response}")  # ДЛЯ ОТЛАДКИ

            # Парсим JSON
            ai_data = json.loads(cleaned_response)

            print(f"🔍 ПАРСИНГ AI: полученные данные: {ai_data}")  # ОТЛАДКА

            # Валидируем ответ
            validation = self._validate_ai_solution(ai_data, expected_solution)

            if not validation['is_valid']:
                return {
                    'success': False,
                    'error': f"AI ответ не прошел валидацию: {validation['error']}"
                }

            # Форматируем финальное объяснение
            explanation = self._format_clean_explanation(ai_data)

            print(f"🔍 ФОРМАТИРОВАННОЕ ОБЪЯСНЕНИЕ: '{explanation}'")  # ОТЛАДКА

            return {
                'success': True,
                'explanation': explanation
            }

        except json.JSONDecodeError as e:
            logger.error(f"Ошибка парсинга JSON от AI: {e}")
            logger.error(f"Ответ AI: {response_text}")

            # Fallback: пытаемся извлечь объяснение даже из невалидного JSON
            try:
                # Ищем explanation в тексте
                explanation_match = re.search(r'"explanation"\s*:\s*"([^"]*)"', response_text)
                if explanation_match:
                    explanation = explanation_match.group(1)
                    return {
                        'success': True,
                        'explanation': f"🎯 ОТВЕТ: {expected_solution}\n\n{explanation}"
                    }
            except:
                pass

            return {'success': False, 'error': 'Неверный формат ответа AI'}
        except Exception as e:
            logger.error(f"Ошибка обработки AI ответа: {e}")
            return {'success': False, 'error': str(e)}

    def _clean_json_response(self, text: str) -> str:
        """Чистит JSON ответ от лишних символов"""
        if not text:
            return "{}"

        # Убираем лишние запятые перед закрывающими скобками
        text = re.sub(r',\s*}', '}', text)
        text = re.sub(r',\s*]', ']', text)

        # Убираем возможные markdown блоки
        text = re.sub(r'```json\s*', '', text)
        text = re.sub(r'\s*```', '', text)

        # Убираем лишние пробелы и переносы в начале/конце
        text = text.strip()

        # Если ответ начинается с переноса строки, убираем его
        text = re.sub(r'^\s*\n', '', text)

        # Проверяем, что это валидный JSON
        if not text.startswith('{'):
            # Пытаемся найти начало JSON
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                text = match.group(0)

        return text

    def _validate_ai_solution(self, ai_data: Dict, expected_solution: str) -> Dict:
        """Проверяет, что AI решение совпадает с SymPy"""
        try:
            ai_solution = str(ai_data.get('solution', '')).strip()
            expected = str(expected_solution).strip()

            print(f"🔍 ВАЛИДАЦИЯ: AI сказал '{ai_solution}'")  # ОТЛАДКА
            print(f"🔍 ВАЛИДАЦИЯ: Ожидали '{expected}'")  # ОТЛАДКА

            # Извлекаем только математическое выражение (игнорируем f'(x) = и т.д.)
            def extract_math_expression(expr: str) -> str:
                # Удаляем префиксы типа f'(x) =, производная =, и т.д.
                expr = re.sub(r'^f\'?\(x\)\s*=\s*', '', expr, flags=re.IGNORECASE)
                expr = re.sub(r'^производная\s*=\s*', '', expr, flags=re.IGNORECASE)
                expr = re.sub(r'^ответ\s*:\s*', '', expr, flags=re.IGNORECASE)
                expr = re.sub(r'^solution\s*:\s*', '', expr, flags=re.IGNORECASE)
                return expr.strip()

            ai_math = extract_math_expression(ai_solution)
            expected_math = extract_math_expression(expected)

            print(f"🔍 ВАЛИДАЦИЯ МАТЕМАТИКА: AI '{ai_math}'")  # ОТЛАДКА
            print(f"🔍 ВАЛИДАЦИЯ МАТЕМАТИКА: Ожидали '{expected_math}'")  # ОТЛАДКА

            # Нормализуем решения для сравнения
            ai_normalized = re.sub(r'[\s*]', '', ai_math).lower()
            expected_normalized = re.sub(r'[\s*]', '', expected_math).lower()

            print(f"🔍 ВАЛИДАЦИЯ НОРМАЛИЗОВАНО: AI '{ai_normalized}'")  # ОТЛАДКА
            print(f"🔍 ВАЛИДАЦИЯ НОРМАЛИЗОВАНО: Ожидали '{expected_normalized}'")  # ОТЛАДКА

            if ai_normalized != expected_normalized:
                return {
                    'is_valid': False,
                    'error': f"Решение AI '{ai_solution}' не совпадает с ожидаемым '{expected}'"
                }

            return {'is_valid': True}

        except Exception as e:
            return {'is_valid': False, 'error': f'Ошибка валидации: {e}'}

    def _format_clean_explanation(self, ai_data: Dict) -> str:
        """Универсальное форматирование AI объяснения"""
        lines = []

        solution = ai_data.get('solution', '')

        # Всегда показываем ответ четко в начале
        lines.append(f"🎯 **ОТВЕТ:** {solution}")
        lines.append("")

        # Основное объяснение
        explanation_text = ai_data.get('explanation', '')
        if explanation_text:
            clean_explanation = re.sub(r'[*_`]', '', str(explanation_text))
            lines.append(clean_explanation)
            lines.append("")

        # Шаги решения
        if ai_data.get('steps') and isinstance(ai_data['steps'], list) and ai_data['steps']:
            lines.append("📋 **Шаги решения:**")
            for i, step in enumerate(ai_data['steps'], 1):
                clean_step = re.sub(r'[*_`]', '', str(step))
                lines.append(f"{i}. {clean_step}")
            lines.append("")

        # Теоретическая справка (только для tutor)
        if ai_data.get('theory') and str(ai_data['theory']).strip():
            theory = re.sub(r'[*_`]', '', str(ai_data['theory']))
            lines.append("📚 **Теоретическая справка:**")
            lines.append(theory)
            lines.append("")

        # Полезные советы (только для tutor)
        if ai_data.get('tips') and isinstance(ai_data['tips'], list) and ai_data['tips']:
            lines.append("💡 **Полезные советы:**")
            for tip in ai_data['tips']:
                clean_tip = re.sub(r'[*_`]', '', str(tip))
                lines.append(f"• {clean_tip}")
            lines.append("")

        # Типичные ошибки (только для tutor)
        if ai_data.get('common_mistakes') and isinstance(ai_data['common_mistakes'], list) and ai_data[
            'common_mistakes']:
            lines.append("⚠️ **Типичные ошибки:**")
            for mistake in ai_data['common_mistakes']:
                clean_mistake = re.sub(r'[*_`]', '', str(mistake))
                lines.append(f"• {clean_mistake}")

        # Объединяем все строки
        explanation = "\n".join(lines).strip()
        explanation = re.sub(r'\n\s*\n', '\n\n', explanation)

        return explanation

    def _create_universal_fallback(self, ai_data: Dict) -> list:
        """Создает универсальное fallback-объяснение для любых типов задач"""
        solution = ai_data.get('solution', '')

        lines = [
            "🔍 Решение математической задачи:",
            "",
            f"Ответ: {solution}",
            "",
            "Общий подход к решению:",
            "1. Проанализируйте тип задачи (производная, интеграл, уравнение и т.д.)",
            "2. Определите подходящий метод решения",
            "3. Примените соответствующие математические правила",
            "4. Проведите вычисления последовательно",
            "5. Проверьте результат",
            "",
            "💡 Советы:",
            "• Внимательно читайте условие задачи",
            "• Определите тип задачи перед началом решения",
            "• Проверяйте каждое преобразование",
            "• Упрощайте ответ если возможно",
            "",
            "⚠️ Частые ошибки:",
            "• Неправильное определение типа задачи",
            "• Ошибки в применении математических правил",
            "• Арифметические ошибки в вычислениях",
            "• Потеря констант в интегралах",
            "• Неправильное применение формул"
        ]

        return lines

    def _format_quick_response(self, sympy_result: Dict, problem_text: str) -> str:
        """Форматирование для быстрого режима"""
        return f"Ответ: {sympy_result['solution']}"

    def _format_sympy_explanation(self, sympy_result: Dict, problem_text: str) -> str:
        """Fallback объяснение через SymPy"""
        lines = [
            f"Задача: {problem_text}",
            "",
            f"Ответ: {sympy_result['solution']}"
        ]

        if sympy_result.get('steps'):
            lines.append("")
            lines.append("Шаги решения:")
            for step in sympy_result['steps']:
                # Убираем Markdown из шагов SymPy
                clean_step = re.sub(r'[*_`]', '', step)
                lines.append(f"- {clean_step}")

        return "\n".join(lines)


# Глобальный экземпляр гибридного решателя
hybrid_solver = HybridSolver()
