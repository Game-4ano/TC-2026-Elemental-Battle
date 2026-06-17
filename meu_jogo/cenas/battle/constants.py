"""
Constantes/helpers compartilhados da tela de batalha.
"""

import pygame
from meu_jogo.core.elements import ELEMENT_COLORS  # noqa: F401 — reexportado para imports existentes


def _to_rgb(color):
    """Converte diferentes formatos de cor para uma tupla (r,g,b) com ints 0-255.
    Fallback para branco se inválido."""
    if isinstance(color, pygame.Color):
        return (color.r, color.g, color.b)
    try:
        # aceita listas/tuplas de números (possivelmente floats)
        seq = tuple(int(max(0, min(255, round(c)))) for c in color)
        if len(seq) >= 3:
            return (seq[0], seq[1], seq[2])
    except Exception:
        pass
    return (255, 255, 255)
