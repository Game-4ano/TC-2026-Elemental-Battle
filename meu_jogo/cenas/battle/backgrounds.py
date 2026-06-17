"""
Fundos temáticos da tela de batalha, um por elemento.
Função pura: recebe surface + element, lê o clock sozinha.
"""

import math
import pygame

from meu_jogo.core.config import SCREEN_WIDTH, SCREEN_HEIGHT


def draw_themed_background(surface: pygame.Surface, element: str) -> None:
    t    = pygame.time.get_ticks() / 1000.0
    w, h = SCREEN_WIDTH, SCREEN_HEIGHT

    _BASE = {
        "Water":    ((5,  15, 60),  (15, 50, 130)),
        "Fire":     ((55,  8,  0),  (100, 28,   5)),
        "Air":      ((22, 18, 55),  (45,  75, 130)),
        "Electric": ((8,   8, 45),  (50,  45,   8)),
        "Dark":     ((3,   2, 14),  (18,   4,  36)),
        "Grass":    ((4,  22,  4),  (15,  65,  15)),
    }
    c1, c2 = _BASE.get(element, ((15, 15, 30), (30, 30, 60)))
    surface.fill(c1)

    # Gradiente horizontal em 5 faixas
    for i in range(5):
        ratio = (i + 1) / 5
        mc    = tuple(int(c1[j] + (c2[j] - c1[j]) * ratio) for j in range(3))
        bnd   = pygame.Surface((w, h // 5), pygame.SRCALPHA)
        bnd.fill((*mc, 50 + i * 10))
        surface.blit(bnd, (0, h - (h // 5) * (i + 1)))

    if element == "Water":
        # Ondas senoidais
        for i in range(3):
            pts = [(x, int(h * 0.55 + 10 * math.sin(t * 1.2 + x * 0.018 + i * 2) + i * 28))
                   for x in range(0, w + 12, 10)]
            if len(pts) >= 2:
                pygame.draw.lines(surface, (30 + i * 10, 110 + i * 20, 200), False, pts, 1)
        # Bolhas subindo
        for i in range(4):
            bx = int((w * (i / 4) + 30 * math.sin(t * 0.6 + i)) % w)
            by = int(h * 0.85 - (t * 28 + i * 55) % (h * 0.65))
            a  = int(55 + 45 * abs(math.sin(t + i)))
            s  = pygame.Surface((7, 7), pygame.SRCALPHA)
            pygame.draw.circle(s, (120, 190, 255, a), (3, 3), 3, 1)
            surface.blit(s, (bx, by))

    elif element == "Fire":
        # Brasas subindo
        for i in range(6):
            bx2 = int((i * w / 6 + t * 30) % w)
            by2 = int(h * 0.85 - abs(math.sin(t * 1.5 + i)) * h * 0.22)
            cv  = int(160 + 95 * abs(math.sin(t * 2 + i)))
            s   = pygame.Surface((4, 4), pygame.SRCALPHA)
            pygame.draw.circle(s, (cv, cv // 3, 0, 150), (2, 2), 2)
            surface.blit(s, (bx2, by2))
        # Silhuetas de rochas no horizonte
        for i in range(5):
            rx = int(w * i / 5)
            rh = int(28 + 18 * abs(math.sin(i * 2.1)))
            pygame.draw.polygon(surface, (22, 8, 0),
                                [(rx, h), (rx + 20, h - rh), (rx + 42, h)])

    elif element == "Electric":
        # Grade de circuito
        for gx in range(0, w, 50):
            a = int(18 + 12 * abs(math.sin(t * 3 + gx * 0.04)))
            ls = pygame.Surface((1, h), pygame.SRCALPHA)
            ls.fill((0, 200, 0, a))
            surface.blit(ls, (gx, 0))
        for gy in range(0, h, 50):
            a = int(18 + 12 * abs(math.sin(t * 3 + gy * 0.04)))
            ls = pygame.Surface((w, 1), pygame.SRCALPHA)
            ls.fill((0, 200, 0, a))
            surface.blit(ls, (0, gy))

    elif element == "Dark":
        # Partículas roxas flutuando
        for i in range(6):
            px2 = int(w * (i / 6) + 20 * math.sin(t * 0.7 + i))
            py2 = int(h * 0.4 + 30 * math.cos(t * 0.5 + i * 1.3))
            a   = int(50 + 60 * abs(math.sin(t * 1.2 + i)))
            s   = pygame.Surface((8, 8), pygame.SRCALPHA)
            pygame.draw.circle(s, (160, 0, 220, a), (4, 4), 4)
            surface.blit(s, (px2, py2))
        # "Olhos" piscando ao fundo
        for i in range(2):
            ex   = int(w * (0.18 + i * 0.58))
            ey   = int(h * 0.28 + 18 * math.sin(t * 0.4 + i))
            abrt = abs(math.sin(t * 0.9 + i * 1.7))
            if abrt > 0.25:
                alpha = int(140 * abrt)
                se    = pygame.Surface((20, 8), pygame.SRCALPHA)
                pygame.draw.ellipse(se, (180, 0, 220, alpha), (0, 0, 20, 8))
                pygame.draw.ellipse(se, (255, 30, 255, alpha), (7, 1, 6, 5))
                surface.blit(se, (ex - 10, ey - 4))

    elif element == "Air":
        # Nuvens passando
        for i in range(3):
            cx2 = int((t * 35 + i * 220) % (w + 120)) - 60
            cy2 = 60 + i * 55
            cs  = pygame.Surface((140, 44), pygame.SRCALPHA)
            pygame.draw.ellipse(cs, (200, 215, 240, 18), (0, 10, 140, 24))
            pygame.draw.ellipse(cs, (210, 225, 250, 14), (20, 0, 100, 30))
            surface.blit(cs, (cx2, cy2))
        # Relâmpago distante ocasional
        if int(t * 2) % 5 == 0:
            lx = int(w * 0.25 + 80 * abs(math.sin(t * 7)))
            pygame.draw.line(surface, (200, 215, 255), (lx, 15), (lx + 8, 65), 1)
            pygame.draw.line(surface, (200, 215, 255), (lx + 8, 65), (lx, 105), 1)

    elif element == "Grass":
        # Folhas caindo
        for i in range(4):
            lx = int((t * 22 + i * 160) % (w + 40))
            ly = int(h * 0.3 + i * 35 + 15 * math.sin(t * 0.8 + i))
            ls = pygame.Surface((6, 18), pygame.SRCALPHA)
            pygame.draw.polygon(ls, (30, 110, 30, 160), [(3, 0), (6, 18), (0, 18)])
            surface.blit(ls, (lx, ly))
