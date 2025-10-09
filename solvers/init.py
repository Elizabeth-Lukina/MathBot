"""
Пакет решателей
"""

from .arithmetic import arithmetic_solver
from .equations import equation_solver
from .derivatives import derivative_solver
from .integrals import integral_solver
from .trigonometry import trigonometry_solver
from .algebra import algebra_solver

__all__ = [
    'arithmetic_solver',
    'equation_solver',
    'derivative_solver',
    'integral_solver',
    'trigonometry_solver',
    'algebra_solver'
]