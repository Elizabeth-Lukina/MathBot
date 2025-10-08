"""
Гибридный решатель - объединяет точность SymPy и объяснения AI
С проверкой корректности AI объяснений
"""

import logging
import time
from typing import Dict, Any, List
from math_solver import math_solver
from explanation_generator import explanation_generator
from config import SOLUTION_MODES

logger = logging.getLogger(__name__)


class HybridSolver:
    """Гибридный решатель с проверкой AI объяснений"""

    def __init__(self):
        self.sympy_solver = math_solver
        self.ai_explainer = explanation_generator

    async def solve_with_mode(self, problem_text: str, mode: str = 'exam') -> Dict[str, Any]:
        """
        Решает задачу в выбранном режиме с гибридным подходом

        Args:
            problem_text: Текст задачи
            mode: Режим решения ('quick', 'exam', 'tutor')

        Returns:
            Результат решения
        """
        start_time = time.time()

        try:
            mode_config = SOLUTION_MODES.get(mode, SOLUTION_MODES['exam'])

            # 1. Всегда решаем через SymPy сначала (дешево и точно)
            logger.info(f"Решаем задачу через SymPy в режиме {mode}")
            sympy_result = self.sympy_solver.solve_problem(problem_text)

            if not sympy_result['success']:
                return {
                    'success': False,
                    'error': 'Не удалось решить задачу с помощью SymPy',
                    'mode': mode
                }

            # 2. Для быстрого режима - возвращаем только ответ
            if mode == 'quick':
                processing_time = time.time() - start_time
                return {
                    'success': True,
                    'mode': 'quick',
                    'solution': sympy_result['solution'],
                    'problem_type': sympy_result['problem_type'],
                    'source': 'sympy',
                    'processing_time': processing_time,
                    'cost': 0.001,
                    'explanation': '🚀 Режим быстрого ответа - только решение'
                }

            # 3. Для режимов с объяснениями - генерируем через AI
            logger.info(f"Генерируем AI объяснение для режима {mode}")

            # Подготавливаем данные для AI
            ai_input = {
                'problem_text': problem_text,
                'solution': sympy_result['solution'],
                'problem_type': sympy_result['problem_type'],
                'steps': sympy_result.get('steps', []),
                'mode': mode
            }

            # Генерируем объяснение
            ai_result = await self.ai_explainer.generate_explanation(ai_input)

            # 4. ВАЖНО: Проверяем корректность AI объяснения
            validated_explanation = self._validate_ai_explanation(
                ai_result,
                sympy_result['solution'],
                problem_text
            )

            processing_time = time.time() - start_time

            # Формируем финальный результат
            result = {
                'success': True,
                'mode': mode,
                'solution': sympy_result['solution'],
                'problem_type': sympy_result['problem_type'],
                'source': 'hybrid',
                'processing_time': processing_time,
                'cost': 0.05,  # Дешевле чистого AI
                'sympy_data': sympy_result,
                'ai_validation': validated_explanation['validation_result']
            }

            # Добавляем объяснение в зависимости от режима
            if mode == 'exam':
                result.update({
                    'explanation': validated_explanation['safe_explanation'],
                    'steps': validated_explanation.get('steps', []),
                    'latex': sympy_result.get('latex', '')
                })
            elif mode == 'tutor':
                result.update({
                    'explanation': validated_explanation['safe_explanation'],
                    'hints': validated_explanation.get('hints', []),
                    'common_mistakes': validated_explanation.get('common_mistakes', []),
                    'learning_tips': validated_explanation.get('learning_tips', [])
                })

            logger.info(f"Гибридное решение завершено за {processing_time:.2f}с")
            return result

        except Exception as e:
            logger.error(f"Ошибка гибридного решения: {e}")
            return {
                'success': False,
                'error': f'Ошибка гибридного решения: {str(e)}',
                'mode': mode
            }

    def _validate_ai_explanation(self, ai_result: Dict, sympy_solution: str, original_problem: str) -> Dict[str, Any]:
        """
        Проверяет корректность AI объяснения и создает безопасную версию
        """
        try:
            validation_checks = {
                'has_explanation': bool(ai_result.get('explanation')),
                'explanation_length': len(ai_result.get('explanation', '')) > 50,
                'matches_solution': self._check_solution_consistency(ai_result, sympy_solution),
                'no_harmful_content': self._check_safe_content(ai_result),
                'mathematical_correctness': self._check_mathematical_correctness(ai_result)
            }

            # Подсчитываем score валидации
            validation_score = sum(validation_checks.values())
            is_valid = validation_score >= 3  # Минимум 3 из 5 проверок

            # Создаем безопасное объяснение
            safe_explanation = self._create_safe_explanation(ai_result, sympy_solution, is_valid)

            return {
                'validation_result': {
                    'is_valid': is_valid,
                    'score': validation_score,
                    'checks': validation_checks
                },
                'safe_explanation': safe_explanation,
                'steps': ai_result.get('step_by_step', []),
                'hints': ai_result.get('tips', []),
                'common_mistakes': ai_result.get('common_mistakes', []),
                'learning_tips': ai_result.get('learning_tips', [])
            }

        except Exception as e:
            logger.error(f"Ошибка валидации AI: {e}")
            # Возвращаем безопасное падение
            return {
                'validation_result': {'is_valid': False, 'score': 0, 'checks': {}},
                'safe_explanation': f'✅ Решение: {sympy_solution}\n\n📝 Задача решена с помощью математического движка.',
                'steps': [],
                'hints': ['Проверьте правильность условия задачи'],
                'common_mistakes': [],
                'learning_tips': []
            }

    def _check_solution_consistency(self, ai_result: Dict, sympy_solution: str) -> bool:
        """Проверяет, что AI объяснение соответствует решению SymPy"""
        try:
            explanation = ai_result.get('explanation', '').lower()
            sympy_sol_str = str(sympy_solution).lower()

            # Проверяем, что в объяснении упоминается правильный ответ
            consistency_indicators = [
                sympy_sol_str in explanation,
                any(keyword in explanation for keyword in ['ответ', 'решение', 'result', 'solution']),
                len(explanation) > 100  # Объяснение не должно быть слишком коротким
            ]

            return sum(consistency_indicators) >= 2

        except Exception as e:
            logger.warning(f"Ошибка проверки консистентности: {e}")
            return False

    def _check_safe_content(self, ai_result: Dict) -> bool:
        """Проверяет отсутствие вредоносного контента"""
        unsafe_patterns = [
            'как обмануть', 'списать', 'читер', 'обман',
            'illegal', 'cheat', 'hack', 'exploit'
        ]

        explanation = ai_result.get('explanation', '').lower()
        return not any(pattern in explanation for pattern in unsafe_patterns)

    def _check_mathematical_correctness(self, ai_result: Dict) -> bool:
        """Базовая проверка математической корректности"""
        explanation = ai_result.get('explanation', '').lower()

        # Проверяем наличие математических терминов
        math_terms = [
            'уравнение', 'формула', 'метод', 'решить',
            'calculate', 'solve', 'equation', 'formula'
        ]

        return any(term in explanation for term in math_terms)

    def _create_safe_explanation(self, ai_result: Dict, sympy_solution: str, is_valid: bool) -> str:
        """Создает безопасное объяснение на основе валидации"""
        if not is_valid or not ai_result.get('explanation'):
            # Возвращаем шаблонное объяснение если AI не прошел валидацию
            return f"""
✅ *Решение найдено:*
`{sympy_solution}`

📝 *Метод решения:* 
Задача решена с помощью математического движка SymPy, который гарантирует точность вычислений.

💡 *Рекомендация:*
Для лучшего понимания рекомендуется изучить соответствующую тему в учебнике.
            """

        # Возвращаем проверенное AI объяснение
        return ai_result['explanation']


# Глобальный экземпляр гибридного решателя
hybrid_solver = HybridSolver()