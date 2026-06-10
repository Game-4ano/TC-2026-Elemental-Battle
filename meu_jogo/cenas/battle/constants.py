"""
Constantes/helpers compartilhados da tela de batalha.

ELEMENT_COLORS e a paleta especifica da batalha (mantida por-tela por decisao
de design; mapa e menu usam paletas proprias).
"""

import pygame

ELEMENT_COLORS = {
    "Fire":     (255, 110,  30),
    "Water":    ( 40, 160, 255),
    "Grass":    ( 70, 210,  70),
    "Electric": (255, 235,  30),
    "Dark":     (150,  40, 220),
    "Air":      (190, 230, 255),
}


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
