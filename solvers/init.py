# Инициализация пакета solvers
from .equation_solver import EquationSolver
from .integral_solver import IntegralSolver
from .derivative_solver import DerivativeSolver
from .trigonometric_solver import TrigonometricSolver
from .system_solver import SystemSolver
from .simplify_solver import SimplifySolver

__all__ = [
    'EquationSolver',
    'IntegralSolver',
    'DerivativeSolver',
    'TrigonometricSolver',
    'SystemSolver',
    'SimplifySolver'
]