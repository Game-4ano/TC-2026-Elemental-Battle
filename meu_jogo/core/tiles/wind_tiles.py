"""Tiles da regiao Vento (Norte) e decorativos da sala do Storm Eagle."""

import math

import pygame

from meu_jogo.core.tiles.base import Tile


class WindTile(Tile):
    def __init__(self, name="Vento", color=(140, 195, 220)):
        super().__init__(name, "Air", color, True, 0)

    def draw(self, surface, x, y, size, offset_x=0, offset_y=0):
        rect = pygame.Rect(x * size - offset_x, y * size - offset_y, size, size)
        pygame.draw.rect(surface, self.color, rect)
        # Linhas curvas simulando vento
        lighter = (min(self.color[0]+30,255), min(self.color[1]+20,255), 255)
        for i in range(2):
            wy = rect.y + size // 3 * (i + 1)
            pygame.draw.line(surface, lighter, (rect.x+2, wy), (rect.x+size-2, wy), 1)
        pygame.draw.rect(surface, (90, 150, 190), rect, 1)


class CloudTile(Tile):
    def __init__(self):
        super().__init__("Nuvem", "Air", (210, 230, 250), True, 0)

    def draw(self, surface, x, y, size, offset_x=0, offset_y=0):
        rect = pygame.Rect(x * size - offset_x, y * size - offset_y, size, size)
        pygame.draw.rect(surface, (170, 200, 230), rect)
        t = pygame.time.get_ticks() / 1000.0
        shift = int(math.sin(t * 0.5 + x * 0.3) * 3)
        pygame.draw.ellipse(surface, (230, 240, 255),
            pygame.Rect(rect.x + 2 + shift, rect.y + size // 3, size - 4, size // 3))
        pygame.draw.ellipse(surface, (200, 220, 245),
            pygame.Rect(rect.x + 4 + shift, rect.y + size // 2, size - 8, size // 4))
        pygame.draw.rect(surface, (150, 180, 210), rect, 1)


class SkyPathTile(Tile):
    def __init__(self):
        super().__init__("Plataforma Celeste", "Air", (200, 215, 235), True, 0)

    def draw(self, surface, x, y, size, offset_x=0, offset_y=0):
        rect = pygame.Rect(x * size - offset_x, y * size - offset_y, size, size)
        pygame.draw.rect(surface, self.color, rect)
        t = pygame.time.get_ticks() / 1000.0
        glow = int(180 + 60 * abs(math.sin(t * 1.2 + x * 0.5)))
        pygame.draw.rect(surface, (glow, glow, 255), rect.inflate(-4, -4), 2)
        pygame.draw.rect(surface, (130, 160, 200), rect, 1)


class WindyGrassTile(Tile):
    def __init__(self):
        super().__init__("Grama Ventosa", "Air", (80, 170, 100), True, 0)

    def draw(self, surface, x, y, size, offset_x=0, offset_y=0):
        rect = pygame.Rect(x * size - offset_x, y * size - offset_y, size, size)
        pygame.draw.rect(surface, self.color, rect)
        t = pygame.time.get_ticks() / 1000.0
        for i in range(4):
            bx = rect.x + size // 5 * (i + 1)
            sway = int(math.sin(t * 3.0 + i * 0.8 + x * 0.4) * 3)
            pygame.draw.line(surface, (50, 140, 60),
                             (bx, rect.y + size - 4),
                             (bx + sway, rect.y + size // 2), 1)
        pygame.draw.rect(surface, (40, 110, 40), rect, 1)


class FeatherTile(Tile):
    def __init__(self):
        super().__init__("Penas", "Air", (230, 235, 245), True, 0)

    def draw(self, surface, x, y, size, offset_x=0, offset_y=0):
        rect = pygame.Rect(x * size - offset_x, y * size - offset_y, size, size)
        pygame.draw.rect(surface, (200, 210, 230), rect)
        t = pygame.time.get_ticks() / 1000.0
        for i in range(2):
            fx = rect.x + size // 3 * (i + 1)
            fy = rect.y + size // 4 + int(math.sin(t * 1.5 + i + x) * 2)
            pygame.draw.line(surface, (255, 255, 255), (fx, fy), (fx + 3, fy + 8), 2)
            pygame.draw.line(surface, (200, 210, 240), (fx, fy), (fx - 3, fy + 8), 1)
        pygame.draw.rect(surface, (160, 175, 200), rect, 1)


class SkyVoidTile(Tile):
    def __init__(self):
        super().__init__("Vazio Celeste", "Air", (100, 140, 200), False, 0)

    def draw(self, surface, x, y, size, offset_x=0, offset_y=0):
        rect = pygame.Rect(x * size - offset_x, y * size - offset_y, size, size)
        pygame.draw.rect(surface, self.color, rect)
        t = pygame.time.get_ticks() / 1000.0
        for i in range(3):
            cx2 = rect.x + (i * 9 + x * 4) % (size - 4) + 2
            cy2 = rect.y + (i * 7 + y * 3) % (size - 4) + 2
            r = int(2 + 2 * abs(math.sin(t * 0.7 + i + x)))
            pygame.draw.circle(surface, (200, 220, 250), (cx2, cy2), r)
        pygame.draw.rect(surface, (70, 110, 170), rect, 1)
