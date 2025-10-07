import logging
import re
from solvers.equation_solver import EquationSolver
from solvers.integral_solver import IntegralSolver
from solvers.derivative_solver import DerivativeSolver
from solvers.trigonometric_solver import TrigonometricSolver
from solvers.system_solver import SystemSolver
from solvers.simplify_solver import SimplifySolver

logger = logging.getLogger(__name__)


class MathSolver:
    def __init__(self):
        self.solvers = {
            'equation': EquationSolver(),
            'integral': IntegralSolver(),
            'derivative': DerivativeSolver(),
            'trigonometric': TrigonometricSolver(),
            'system': SystemSolver(),
            'expression': SimplifySolver()
        }
        logger.info("MathSolver инициализирован с подключаемыми решателями")

    def solve_with_steps(self, problem_text):
        """Основной метод решения"""
        logger.debug(f"Решение задачи: {problem_text}")

        try:
            cleaned_text = self.clean_text(problem_text)
            problem_type = self.detect_problem_type(cleaned_text)

            # Выбираем соответствующий решатель
            solver = self.solvers.get(problem_type, self.solvers['expression'])
            return solver.solve_with_steps(cleaned_text)

        except Exception as e:
            logger.error(f"Ошибка в MathSolver: {e}")
            return {
                'success': False,
                'error': f'Системная ошибка: {str(e)}'
            }

    def detect_problem_type(self, text):
        """Определение типа задачи"""
        text_lower = text.lower()

        if any(word in text_lower for word in ['∫', 'integral', 'интеграл']):
            return 'integral'
        if any(word in text_lower for word in ['derivative', 'производная', 'd/d']):
            return 'derivative'
        if ('\n' in text and '=' in text) or (';' in text and '=' in text):
            return 'system'
        trig_funcs = ['sin', 'cos', 'tan', 'cot', 'sec', 'csc', 'тригонометр']
        if any(func in text_lower for func in trig_funcs) and '=' in text_lower:
            return 'trigonometric'
        if '=' in text_lower:
            return 'equation'
        return 'expression'

    def clean_text(self, text):
        """Очистка текста"""
        if not text:
            return ""

        replacements = {
            '^': '**', '×': '*', '÷': '/', '–': '-', '—': '-',
            'π': 'pi', '∞': 'oo', '√': 'sqrt', '²': '**2', '³': '**3'
        }

        cleaned = text
        for old, new in replacements.items():
            cleaned = cleaned.replace(old, new)

        cleaned = re.sub(r'\s*([+\-*/=()])\s*', r'\1', cleaned)
        cleaned = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', cleaned)
        cleaned = re.sub(r'([a-zA-Z])(\d)', r'\1*\2', cleaned)

        return cleaned.strip()


# Глобальный экземпляр
math_solver = MathSolver()