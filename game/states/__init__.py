"""
Estados del juego para Gridfall.
Cada estado maneja su propia lógica y renderizado.
"""

from .in_game import manejar_estado_en_juego
from .confirmar_salir import manejar_estado_confirmar_salir
from .fin_del_juego import manejar_estado_fin_juego

__all__ = [
    'manejar_estado_en_juego',
    'manejar_estado_confirmar_salir',
    'manejar_estado_fin_juego',
]