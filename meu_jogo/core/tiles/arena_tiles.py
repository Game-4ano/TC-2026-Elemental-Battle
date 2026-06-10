"""Tiles de chao das arenas de batalha (gelo, vulcao, celeste, metalica)."""

import math

import pygame

from meu_jogo.core.tiles.base import Tile


class IceArenaTile(Tile):
    def __init__(self):
        super().__init__("Arena de Gelo", "Water", (160, 210, 240), True, 0)

    def draw(self, surface, x, y, size, offset_x=0, offset_y=0):
        rect = pygame.Rect(x * size - offset_x, y * size - offset_y, size, size)
        pygame.draw.rect(surface, self.color, rect)
        t = pygame.time.get_ticks() / 1000.0
        alpha = int(30 + 20 * math.sin(t * 1.5 + x * 0.6 + y * 0.4))
        pygame.draw.rect(surface, (200, 240, 255), rect.inflate(-alpha // 3, -alpha // 3), 1)
        pygame.draw.rect(surface, (100, 170, 210), rect, 1)


class VolcanoFloorTile(Tile):
    def __init__(self):
        super().__init__("Chão Vulcânico", "Fire", (40, 25, 15), True, 0)

    def draw(self, surface, x, y, size, offset_x=0, offset_y=0):
        rect = pygame.Rect(x * size - offset_x, y * size - offset_y, size, size)
        pygame.draw.rect(surface, self.color, rect)
        t = pygame.time.get_ticks() / 1000.0
        for i in range(3):
            cx2 = rect.x + (i * 8 + x * 5) % (size - 4) + 2
            cy2 = rect.y + (i * 6 + y * 4) % (size - 4) + 2
            glow = int(80 + 80 * abs(math.sin(t * 2.0 + i + x * 0.3)))
            pygame.draw.line(surface, (glow, glow // 3, 0), (cx2, cy2), (cx2 + 5, cy2 + 3), 1)
        pygame.draw.rect(surface, (20, 10, 5), rect, 1)


class SkyArenaTile(Tile):
    def __init__(self):
        super().__init__("Arena Celeste", "Air", (195, 215, 240), True, 0)

    def draw(self, surface, x, y, size, offset_x=0, offset_y=0):
        rect = pygame.Rect(x * size - offset_x, y * size - offset_y, size, size)
        pygame.draw.rect(surface, self.color, rect)
        t = pygame.time.get_ticks() / 1000.0
        glow = int(200 + 55 * abs(math.sin(t * 0.8 + x * 0.4)))
        pygame.draw.rect(surface, (glow, glow, 255), rect.inflate(-6, -6), 2)
        pygame.draw.rect(surface, (140, 170, 210), rect, 1)


class MetalArenaTile(Tile):
    def __init__(self):
        super().__init__("Arena Metálica", "Electric", (120, 130, 150), True, 0)

    def draw(self, surface, x, y, size, offset_x=0, offset_y=0):
        rect = pygame.Rect(x * size - offset_x, y * size - offset_y, size, size)
        pygame.draw.rect(surface, self.color, rect)
        t = pygame.time.get_ticks() / 1000.0
        glow = int(50 + 50 * abs(math.sin(t * 2.0 + x * 0.5 + y * 0.3)))
        pygame.draw.rect(surface, (80, 100, 130 + glow // 3), rect.inflate(-4, -4), 1)
        cx2, cy2 = rect.centerx, rect.centery
        hs = size // 4
        pts = [(cx2, cy2 - hs), (cx2 + hs, cy2), (cx2, cy2 + hs), (cx2 - hs, cy2)]
        pygame.draw.polygon(surface, (150, 160, 180), pts, 1)
        pygame.draw.rect(surface, (80, 90, 110), rect, 1)
