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
            self.client = OpenAI(api_key=self.api_key)

        # the newest OpenAI model is "gpt-5" which was released August 7, 2025.
        # do not change this unless explicitly requested by the user
        # Adding fallback models for better reliability
        self.models = ["gpt-5", "gpt-4o", "gpt-4-turbo", "gpt-4"]
        self.model = OPENAI_MODEL
        self.max_tokens = OPENAI_MAX_TOKENS
        self.temperature = OPENAI_TEMPERATURE

    def generate_explanation(self, problem_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Генерация подробного объяснения решения математической задачи
        
        Args:
            problem_data: Данные о задаче и её решении
            
        Returns:
            Словарь с объяснением и метаданными
        """
        if not self.client:
            return {
                'success': False,
                'error': 'OpenAI API недоступен - отсутствует API ключ'
            }

        start_time = time.time()

        try:
            # Формируем промпт для генерации объяснения
            prompt = self._create_explanation_prompt(problem_data)

            logger.info("Отправляем запрос в OpenAI для генерации объяснения")

            # Пробуем модели по порядку до успешного ответа
            response = None
            for model_name in self.models:
                try:
                    response = self.client.chat.completions.create(
                        model=model_name,
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
                        temperature=self.temperature,
                        response_format={"type": "json_object"}
                    )
                    logger.info(f"Успешно использована модель: {model_name}")
                    break
                except Exception as model_error:
                    logger.warning(f"Модель {model_name} недоступна: {model_error}")
                    continue

            if not response:
                raise Exception("Все модели OpenAI недоступны")

            # Парсим ответ
            response_text = response.choices[0].message.content or '{}'
            explanation_data = json.loads(response_text)

            processing_time = time.time() - start_time

            # Подсчитываем стоимость (приблизительно)
            prompt_tokens = response.usage.prompt_tokens if response.usage else 0
            completion_tokens = response.usage.completion_tokens if response.usage else 0
            estimated_cost = self._estimate_cost(prompt_tokens, completion_tokens)

            logger.info(
                f"Объяснение сгенерировано за {processing_time:.2f}с, токены: {prompt_tokens}/{completion_tokens}")

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
        """
        Решение сложных математических задач с помощью OpenAI
        Используется когда SymPy не может решить задачу
        
        Args:
            problem_text: Текст математической задачи
            
        Returns:
            Словарь с решением и объяснением
        """
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

    # В explanation_generator.py обновляем промпты:

    def _get_system_prompt(self) -> str:
        """Системный промпт для генерации объяснений с учетом режимов"""
        return """
    Ты - эксперт по математике, который объясняет решения задач простым и понятным языком на русском языке.

    Доступные режимы:
    1. 📚 ЭКЗАМЕН - подробное пошаговое решение с объяснениями
    2. 👨‍🏫 РЕПЕТИТОР - обучающее объяснение с подсказками и советами

    Формат ответа JSON:
    {
        "explanation": "Основное объяснение решения",
        "steps": ["Шаг 1", "Шаг 2", ...],
        "tips": ["Совет 1", "Совет 2", ...],
        "common_mistakes": ["Типичная ошибка 1", ...],
        "learning_tips": ["Как лучше запомнить", ...]
    }

    Для режима ЭКЗАМЕН: делай акцент на точности и полноте шагов.
    Для режима РЕПЕТИТОР: добавляй обучающие элементы и подсказки.
        """

    def _create_explanation_prompt(self, problem_data: Dict[str, Any]) -> str:
        """Создание промпта с учетом режима"""
        mode = problem_data.get('mode', 'exam')
        mode_descriptions = {
            'exam': 'Режим ЭКЗАМЕН - нужны точные пошаговые объяснения',
            'tutor': 'Режим РЕПЕТИТОР - нужны обучающие объяснения с подсказками'
        }

        prompt = f"""
    {mode_descriptions.get(mode, '')}

    Задача: {problem_data.get('problem_text', '')}
    Решение: {problem_data.get('solution', '')}
    Тип задачи: {problem_data.get('problem_type', '')}

    Шаги решения SymPy:
    {chr(10).join(f"{i + 1}. {step}" for i, step in enumerate(problem_data.get('steps', []))) if problem_data.get('steps') else "Нет подробных шагов"}

    Создай объяснение в соответствии с выбранным режимом.
        """

        return prompt

    def _get_solving_system_prompt(self) -> str:
        """Системный промпт для решения задач"""
        return """
Ты - математический эксперт, который решает сложные математические задачи.

Твоя задача:
1. Проанализировать математическую задачу
2. Определить тип задачи и метод решения
3. Решить задачу пошагово
4. Предоставить объяснение решения
5. Оформить результат в LaTeX

ВАЖНО: Отвечай ТОЛЬКО в формате JSON:
{
    "solvable": true/false,
    "problem_type": "тип задачи",
    "solution": "финальный ответ",
    "steps": ["подробные шаги решения"],
    "explanation": "объяснение метода решения",
    "latex": "LaTeX формула решения"
}

Если задача не может быть решена, установи "solvable": false и объясни почему.
Используй русский язык для всех текстовых полей.
        """

    def _create_explanation_prompt(self, problem_data: Dict[str, Any]) -> str:
        """Создание промпта для объяснения решения"""
        problem_text = problem_data.get('problem_text', '')
        solution = problem_data.get('solution', '')
        problem_type = problem_data.get('problem_type', '')
        steps = problem_data.get('steps', [])

        prompt = f"""
Задача: {problem_text}

Решение получено с помощью SymPy:
Тип задачи: {problem_type}
Ответ: {solution}

Шаги решения:
{chr(10).join(f"{i + 1}. {step}" for i, step in enumerate(steps)) if steps else "Нет подробных шагов"}

Создай подробное объяснение этого решения для студента, который изучает математику. 
Объясни каждый шаг, используемые методы и концепции.
Добавь практические советы для решения подобных задач.
        """

        return prompt

    def _create_solving_prompt(self, problem_text: str) -> str:
        """Создание промпта для решения задачи"""
        return f"""
Реши следующую математическую задачу:

{problem_text}

Проанализируй задачу, определи тип и метод решения, затем реши её пошагово.
Если задача не может быть решена или некорректна, укажи это в ответе.
        """

    def _estimate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
        """
        Приблизительная оценка стоимости запроса
        Цены могут изменяться, это только для внутренней аналитики
        """
        # Примерные цены для GPT-5 (в USD за 1000 токенов)
        # Реальные цены могут отличаться
        prompt_cost_per_1k = 0.03
        completion_cost_per_1k = 0.06

        prompt_cost = (prompt_tokens / 1000) * prompt_cost_per_1k
        completion_cost = (completion_tokens / 1000) * completion_cost_per_1k

        return prompt_cost + completion_cost


# Создаем глобальный экземпляр генератора объяснений
explanation_generator = ExplanationGenerator()
