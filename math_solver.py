"""
Главный математический решатель - роутер к специализированным решателям
"""

import logging
import time
import re
from typing import Dict, Any

# Импортируем решатели напрямую из папки solvers
from solvers.arithmetic import arithmetic_solver
from solvers.equations import equation_solver
from solvers.derivatives import derivative_solver
from solvers.integrals import integral_solver
from solvers.trigonometry import trigonometry_solver
from solvers.algebra import algebra_solver
logger = logging.getLogger(__name__)

class MathSolver:
    """Главный решатель - роутер к специализированным решателям"""

    def solve_problem(self, problem_text: str) -> Dict[str, Any]:
        """
        Основная функция решения математической задачи
        Определяет тип и направляет в соответствующий решатель
        """
        start_time = time.time()

        try:
            logger.info(f"=== НОВАЯ ЗАДАЧА: {problem_text} ===")

            # Определяем тип задачи
            problem_type = self._detect_problem_type(problem_text)
            logger.info(f"Определен тип задачи: {problem_type}")

            # Направляем в соответствующий решатель
            result = None
            if problem_type == "arithmetic":
                result = arithmetic_solver.solve(problem_text)
            elif problem_type == "equation":
                result = equation_solver.solve(problem_text)
            elif problem_type == "derivative":
                result = derivative_solver.solve(problem_text)
            elif problem_type == "integral":
                result = integral_solver.solve(problem_text)
            elif problem_type == "trigonometry":
                result = trigonometry_solver.solve(problem_text)
            elif problem_type == "algebra":
                result = algebra_solver.solve(problem_text)
            else:
                # Fallback на арифметику
                result = arithmetic_solver.solve(problem_text)

            processing_time = time.time() - start_time

            if result and result.get('success'):
                return {
                    'success': True,
                    'problem_type': problem_type,
                    'solution': result['solution'],
                    'steps': result.get('steps', []),
                    'latex': result.get('latex', ''),
                    'method': 'sympy',
                    'processing_time': processing_time,
                    'explanation': result.get('explanation', '')
                }
            else:
                return {
                    'success': False,
                    'problem_type': problem_type,
                    'method': 'sympy',
                    'processing_time': processing_time,
                    'error': result.get('explanation', 'Не удалось решить задачу') if result else 'Не удалось решить задачу'
                }

        except Exception as e:
            processing_time = time.time() - start_time
            logger.error(f"Ошибка решения задачи: {e}")
            return {
                'success': False,
                'method': 'sympy',
                'processing_time': processing_time,
                'error': str(e)
            }

    def _detect_problem_type(self, text: str) -> str:
        """Определение типа математической задачи"""
        text_lower = text.lower()

        if any(word in text_lower for word in ['производн', 'дифференц', 'f\'', 'd/dx', 'dy/dx']):
            return 'derivative'

        if re.search(r'f\s*\(\s*x\s*\)\s*=', text, re.IGNORECASE):
            return 'derivative'

        if any(word in text_lower for word in ['интеграл', '∫', 'проинтегрир']):
            return 'integral'

        if '=' in text:
            return 'equation'

        if any(word in text_lower for word in ['sin', 'cos', 'tan', 'tg', 'ctg', 'тригонометр']):
            return 'trigonometry'

        if any(word in text_lower for word in ['упростить', 'разложить', 'алгебр']):
            return 'algebra'

        return 'arithmetic'

# Глобальный экземпляр решателя
math_solver = MathSolver()