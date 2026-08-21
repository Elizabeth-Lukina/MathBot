"""
Модуль для генерации объяснений математических решений
Использует OpenAI API для создания подробных объяснений на русском языке
"""

import os
import json
import logging
import time
from typing import Dict, List, Optional, Any
from openai import OpenAI
from config import OPENAI_MODEL, OPENAI_MAX_TOKENS, OPENAI_TEMPERATURE

logger = logging.getLogger(__name__)


class ExplanationGenerator:
    """Класс для генерации объяснений с помощью OpenAI"""

    def __init__(self):
        self.api_key = os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            logger.warning("OPENAI_API_KEY не установлен")
            self.client = None
        else:
            # Используем proxyapi.ru
            self.client = OpenAI(
                api_key=self.api_key,
                base_url="https://api.proxyapi.ru"
            )

        self.model = OPENAI_MODEL
        self.max_tokens = OPENAI_MAX_TOKENS
        self.temperature = OPENAI_TEMPERATURE

    def generate_explanation(self, problem_data: Dict[str, Any]) -> Dict[str, Any]:
        """Генерация подробного объяснения решения математической задачи"""
        if not self.client:
            return {
                'success': False,
                'error': 'OpenAI API недоступен'
            }

        start_time = time.time()

        try:
            prompt = self._create_explanation_prompt(problem_data)
            logger.info("Генерируем объяснение через OpenAI")

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )

            # Парсим ответ
            response_text = response.choices[0].message.content or '{}'
            explanation_data = json.loads(response_text)

            processing_time = time.time() - start_time

            # Подсчитываем стоимость
            prompt_tokens = response.usage.prompt_tokens if response.usage else 0
            completion_tokens = response.usage.completion_tokens if response.usage else 0
            estimated_cost = self._estimate_cost(prompt_tokens, completion_tokens)

            logger.info(f"Объяснение сгенерировано за {processing_time:.2f}с")

            return {
                'success': True,
                'explanation': explanation_data.get('explanation', ''),
                'step_by_step': explanation_data.get('steps', []),
                'latex_formatted': explanation_data.get('latex', ''),
                'difficulty': explanation_data.get('difficulty', 'средний'),
                'concept': explanation_data.get('concept', ''),
                'tips': explanation_data.get('tips', []),
                'processing_time': processing_time,
                'tokens_used': prompt_tokens + completion_tokens,
                'estimated_cost': estimated_cost
            }

        except json.JSONDecodeError as e:
            logger.error(f"Ошибка парсинга JSON ответа от OpenAI: {e}")
            return {
                'success': False,
                'error': 'Ошибка обработки ответа от AI'
            }
        except Exception as e:
            logger.error(f"Ошибка генерации объяснения: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def solve_complex_problem(self, problem_text: str) -> Dict[str, Any]:
        """Решение сложных математических задач с помощью OpenAI"""
        if not self.client:
            return {
                'success': False,
                'error': 'OpenAI API недоступен'
            }

        start_time = time.time()

        try:
            prompt = self._create_solving_prompt(problem_text)
            logger.info("Отправляем запрос в OpenAI для решения сложной задачи")

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": self._get_solving_system_prompt()
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                response_format={"type": "json_object"}
            )

            response_text = response.choices[0].message.content or '{}'
            solution_data = json.loads(response_text)

            processing_time = time.time() - start_time

            # Подсчитываем стоимость
            prompt_tokens = response.usage.prompt_tokens if response.usage else 0
            completion_tokens = response.usage.completion_tokens if response.usage else 0
            estimated_cost = self._estimate_cost(prompt_tokens, completion_tokens)

            return {
                'success': solution_data.get('solvable', False),
                'solution': solution_data.get('solution', ''),
                'steps': solution_data.get('steps', []),
                'explanation': solution_data.get('explanation', ''),
                'latex': solution_data.get('latex', ''),
                'problem_type': solution_data.get('problem_type', 'неизвестный'),
                'method': 'openai',
                'processing_time': processing_time,
                'tokens_used': prompt_tokens + completion_tokens,
                'estimated_cost': estimated_cost
            }

        except Exception as e:
            logger.error(f"Ошибка решения через OpenAI: {e}")
            return {
                'success': False,
                'error': str(e),
                'method': 'openai'
            }

    def _get_system_prompt(self) -> str:
        """Системный промпт для генерации объяснений"""
        return """Ты - эксперт по математике, который объясняет решения задач простым и понятным языком на русском языке.

Формат ответа JSON:
{
    "explanation": "Основное объяснение решения",
    "steps": ["Шаг 1", "Шаг 2", ...],
    "tips": ["Совет 1", "Совет 2", ...],
    "common_mistakes": ["Типичная ошибка 1", ...],
    "learning_tips": ["Как лучше запомнить", ...]
}"""

    def _create_explanation_prompt(self, problem_data: Dict[str, Any]) -> str:
        """Создание промпта для объяснения решения"""
        problem_text = problem_data.get('problem_text', '')
        solution = problem_data.get('solution', '')
        problem_type = problem_data.get('problem_type', '')
        steps = problem_data.get('steps', [])

        prompt = f"""Задача: {problem_text}

Решение: {solution}
Тип задачи: {problem_type}

Шаги решения:
{chr(10).join(f"{i + 1}. {step}" for i, step in enumerate(steps)) if steps else "Нет подробных шагов"}

Создай подробное объяснение этого решения для студента."""

        return prompt

    def _get_solving_system_prompt(self) -> str:
        """Системный промпт для решения задач"""
        return """Ты - математический эксперт, который решает сложные математические задачи.

Формат ответа JSON:
{
    "solvable": true/false,
    "problem_type": "тип задачи",
    "solution": "финальный ответ",
    "steps": ["подробные шаги решения"],
    "explanation": "объяснение метода решения",
    "latex": "LaTeX формула решения"
}

Используй русский язык для всех текстовых полей."""

    def _create_solving_prompt(self, problem_text: str) -> str:
        """Создание промпта для решения задачи"""
        return f"Реши математическую задачу: {problem_text}"

    def _estimate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """Приблизительная оценка стоимости запроса"""
        prompt_cost_per_1k = 0.03
        completion_cost_per_1k = 0.06

        prompt_cost = (prompt_tokens / 1000) * prompt_cost_per_1k
        completion_cost = (completion_tokens / 1000) * completion_cost_per_1k

        return prompt_cost + completion_cost


# Создаем глобальный экземпляр генератора объяснений
explanation_generator = ExplanationGenerator()
