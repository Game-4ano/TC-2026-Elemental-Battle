"""Tiles da regiao Sombra e da sala do Shadow Lord."""

import math

import pygame

from meu_jogo.core.tiles.base import Tile


class VoidFloorTile(Tile):
    def __init__(self):
        super().__init__("Chão do Vazio", "Dark", (15, 8, 28), True, 0)

    def draw(self, surface, grid_pos, size, camera_offset):
        rect = self._screen_rect(grid_pos, size, camera_offset)
        pygame.draw.rect(surface, self.color, rect)
        t = pygame.time.get_ticks() / 1000.0
        gx, gy = int(grid_pos.x), int(grid_pos.y)
        for i in range(3):
            px2 = rect.x + (i * 9 + gx * 5) % (size - 4) + 2
            py2 = rect.y + (i * 7 + gy * 3) % (size - 4) + 2
            pulse = abs(math.sin(t * 2.5 + i + gx * 0.4 + gy * 0.3))
            r = int(1 + 2 * pulse)
            cv = int(80 + 120 * pulse)
            pygame.draw.circle(surface, (cv // 2, 0, cv), (px2, py2), r)
        pygame.draw.rect(surface, (30, 5, 50), rect, 1)


class ShadowCrystalTile(Tile):
    def __init__(self):
        super().__init__("Cristal das Sombras", "Dark", (60, 10, 100), False, 0)

    def draw(self, surface, grid_pos, size, camera_offset):
        rect = self._screen_rect(grid_pos, size, camera_offset)
        pygame.draw.rect(surface, (10, 3, 20), rect)
        t = pygame.time.get_ticks() / 1000.0
        gx, gy = int(grid_pos.x), int(grid_pos.y)
        glow = int(80 + 120 * abs(math.sin(t * 1.8 + gx + gy)))
        cx2, cy2 = rect.centerx, rect.centery
        pts = [(cx2, rect.y + 2), (rect.x + size - 4, cy2 - 2),
               (cx2, rect.y + size - 2), (rect.x + 4, cy2 + 2)]
        pygame.draw.polygon(surface, (glow // 2, 0, glow), pts)
        pygame.draw.polygon(surface, (180, 100, 255), pts, 1)
        # Olho que abre/fecha esporadicamente
        eye_phase = abs(math.sin(t * 0.55 + gx * 1.4 + gy * 0.85))
        if eye_phase > 0.78:
            ea = int(220 * (eye_phase - 0.78) / 0.22)
            es = pygame.Surface((10, 5), pygame.SRCALPHA)
            pygame.draw.ellipse(es, (140, 0, 200, ea), (0, 0, 10, 5))
            pygame.draw.circle(es, (255, 30, 255, ea), (5, 2), 2)
            surface.blit(es, (rect.x + size // 2 - 5, rect.y + size // 2 - 2))


class TwilightTile(Tile):
    """Transicao gradual entre o Vazio Sombrio e o Ceu dos Ventos — a cor
    interpola entre o roxo do vazio e o azul da nuvem conforme `blend`
    (0.0 = quase vazio, 1.0 = quase ceu), pra sumir o corte seco entre os
    dois biomas."""

    _VOID_COLOR  = (15, 8, 28)
    _CLOUD_COLOR = (210, 230, 250)

    def __init__(self, blend: float):
        self.blend = max(0.0, min(1.0, blend))
        color = tuple(
            int(v + (c - v) * self.blend)
            for v, c in zip(self._VOID_COLOR, self._CLOUD_COLOR)
        )
        super().__init__("Crepúsculo", "Air", color, True, 0)

    def draw(self, surface, grid_pos, size, camera_offset):
        rect = self._screen_rect(grid_pos, size, camera_offset)
        pygame.draw.rect(surface, self.color, rect)
        t = pygame.time.get_ticks() / 1000.0

        if self.blend < 0.7:   # particulas roxas, mais fortes perto do vazio
            gx, gy = int(grid_pos.x), int(grid_pos.y)
            px2 = rect.x + (gx * 9) % (size - 4) + 2
            py2 = rect.y + (gy * 7) % (size - 4) + 2
            pulse = abs(math.sin(t * 2.0 + gx * 0.4 + gy * 0.3))
            a = int(160 * (1.0 - self.blend) * pulse)
            if a > 0:
                s = pygame.Surface((4, 4), pygame.SRCALPHA)
                pygame.draw.circle(s, (160, 0, 220, a), (2, 2), 2)
                surface.blit(s, (px2 - 2, py2 - 2))

        if self.blend > 0.3:   # nevoa de nuvem, mais forte perto do ceu
            a = int(150 * self.blend)
            cs = pygame.Surface((size - 4, size // 3), pygame.SRCALPHA)
            pygame.draw.ellipse(cs, (230, 240, 255, a), cs.get_rect())
            surface.blit(cs, (rect.x + 2, rect.y + size // 3))

        pygame.draw.rect(surface, tuple(max(0, c - 30) for c in self.color), rect, 1)


class DarkMistTile(Tile):
    def __init__(self):
        super().__init__("Névoa Sombria", "Dark", (25, 10, 40), True, 0)

    def draw(self, surface, grid_pos, size, camera_offset):
        rect = self._screen_rect(grid_pos, size, camera_offset)
        pygame.draw.rect(surface, self.color, rect)
        t = pygame.time.get_ticks() / 1000.0
        gx, gy = int(grid_pos.x), int(grid_pos.y)
        alpha_factor = abs(math.sin(t * 1.2 + gx * 0.5 + gy * 0.4))
        mc = int(60 + 80 * alpha_factor)
        pygame.draw.ellipse(surface, (mc // 3, 0, mc),
            pygame.Rect(rect.x + 3, rect.y + size // 3, size - 6, size // 3))
        pygame.draw.rect(surface, (15, 5, 25), rect, 1)
