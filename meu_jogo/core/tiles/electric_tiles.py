"""Tiles da regiao Eletrica (Sul) e decorativos da sala do Thunder Beast."""

import math

import pygame

from meu_jogo.core.tiles.base import Tile


class SandTile(Tile):
    tile_sprite_key = "sand"

    def __init__(self):
        super().__init__("Areia", "Electric", (210, 190, 100), True, 0)

    def draw(self, surface, x, y, size, offset_x=0, offset_y=0):
        rect = pygame.Rect(x * size - offset_x, y * size - offset_y, size, size)
        pygame.draw.rect(surface, self.color, rect)
        for i in range(5):
            px2 = rect.x + (i * 6 + x * 4) % (size - 2)
            py2 = rect.y + (i * 5 + y * 3) % (size - 2)
            pygame.draw.circle(surface, (180, 160, 70), (px2, py2), 1)
        pygame.draw.rect(surface, (170, 150, 60), rect, 1)


class ChargedSandTile(Tile):
    def __init__(self):
        super().__init__("Areia Carregada", "Electric", (190, 175, 60), True, 0)

    def draw(self, surface, x, y, size, offset_x=0, offset_y=0):
        rect = pygame.Rect(x * size - offset_x, y * size - offset_y, size, size)
        pygame.draw.rect(surface, (190, 175, 60), rect)
        t = pygame.time.get_ticks() / 1000.0
        for i in range(2):
            if math.sin(t * 8.0 + i * 1.5 + x * 0.7 + y * 0.4) > 0.6:
                lx = rect.x + (i * 11 + x * 3) % (size - 8) + 4
                ly = rect.y + (i * 8 + y * 5) % (size - 8) + 4
                pygame.draw.line(surface, (255, 255, 80),
                                 (lx, ly), (lx + 4, ly - 4), 1)
                pygame.draw.line(surface, (255, 255, 80),
                                 (lx + 4, ly - 4), (lx + 2, ly - 8), 1)
        pygame.draw.rect(surface, (150, 135, 30), rect, 1)


class MetalTile(Tile):
    def __init__(self):
        super().__init__("Metal", "Electric", (150, 155, 170), True, 0)

    def draw(self, surface, x, y, size, offset_x=0, offset_y=0):
        rect = pygame.Rect(x * size - offset_x, y * size - offset_y, size, size)
        pygame.draw.rect(surface, self.color, rect)
        refl = (200, 205, 220)
        pygame.draw.line(surface, refl, (rect.x, rect.y), (rect.x+size, rect.y), 1)
        pygame.draw.line(surface, refl, (rect.x, rect.y), (rect.x, rect.y+size), 1)
        pygame.draw.rect(surface, (100, 105, 120), rect, 1)


class LightningCrystalTile(Tile):
    def __init__(self):
        super().__init__("Cristal Raio", "Electric", (220, 200, 20), False, 0)

    def draw(self, surface, x, y, size, offset_x=0, offset_y=0):
        rect = pygame.Rect(x * size - offset_x, y * size - offset_y, size, size)
        pygame.draw.rect(surface, (100, 90, 10), rect)
        t = pygame.time.get_ticks() / 1000.0
        glow = int(150 + 105 * abs(math.sin(t * 4.0 + x + y)))
        cx2, cy2 = rect.centerx, rect.centery
        pts = [(cx2, rect.y+2), (rect.x+size-3, cy2), (cx2, rect.y+size-2), (rect.x+3, cy2)]
        pygame.draw.polygon(surface, (glow, glow, 0), pts)
        pygame.draw.polygon(surface, (255, 255, 180), pts, 1)


class CircuitFloorTile(Tile):
    def __init__(self):
        super().__init__("Chão de Circuito", "Electric", (30, 38, 50), True, 0)

    def draw(self, surface, x, y, size, offset_x=0, offset_y=0):
        rect = pygame.Rect(x * size - offset_x, y * size - offset_y, size, size)
        pygame.draw.rect(surface, self.color, rect)
        t = pygame.time.get_ticks() / 1000.0
        # Linhas de circuito estáticas
        cx2, cy2 = rect.x + size // 2, rect.y + size // 2
        pygame.draw.line(surface, (0, 80, 60), (rect.x, cy2), (rect.right, cy2), 1)
        pygame.draw.line(surface, (0, 80, 60), (cx2, rect.y), (cx2, rect.bottom), 1)
        # Nó central pulsante
        pulse = abs(math.sin(t * 2.5 + x * 0.4 + y * 0.3))
        cv    = int(60 + 140 * pulse)
        pygame.draw.circle(surface, (0, cv, cv // 2), (cx2, cy2), 3)
        # Pulsos viajando pelas linhas
        prog = (t * 1.8 + x * 0.25 + y * 0.2) % 1.0
        px2  = rect.x + int(prog * size)
        pygame.draw.circle(surface, (0, 200, 120), (px2, cy2), 2)
        pygame.draw.rect(surface, (20, 55, 40), rect, 1)


class NeonBorderTile(Tile):
    def __init__(self):
        super().__init__("Tubo Neon", "Electric", (20, 20, 30), False, 0)

    def draw(self, surface, x, y, size, offset_x=0, offset_y=0):
        rect = pygame.Rect(x * size - offset_x, y * size - offset_y, size, size)
        pygame.draw.rect(surface, (15, 15, 25), rect)
        t   = pygame.time.get_ticks() / 1000.0
        gv  = int(100 + 155 * abs(math.sin(t * 2.0 + x * 0.5 + y * 0.4)))
        pygame.draw.rect(surface, (0, gv, gv // 3),
                         rect.inflate(-6, -6), 2, border_radius=3)
        pygame.draw.rect(surface, (10, 10, 20), rect, 1)


class BoltTile(Tile):
    def __init__(self):
        super().__init__("Parafuso Metálico", "Electric", (80, 80, 100), True, 0)

    def draw(self, surface, x, y, size, offset_x=0, offset_y=0):
        rect = pygame.Rect(x * size - offset_x, y * size - offset_y, size, size)
        pygame.draw.rect(surface, (38, 38, 52), rect)
        t = pygame.time.get_ticks() / 1000.0
        glow = int(90 + 80 * abs(math.sin(t * 2.2 + x * 0.5 + y * 0.4)))
        cx, cy = rect.centerx, rect.centery
        pts = [(cx + int(6 * math.cos(i * math.pi / 3)),
                cy + int(6 * math.sin(i * math.pi / 3))) for i in range(6)]
        pygame.draw.polygon(surface, (glow, glow, glow + 20), pts)
        pygame.draw.polygon(surface, (200, 200, 255), pts, 1)
        pygame.draw.circle(surface, (glow // 2, glow // 2, glow), (cx, cy), 2)
        pygame.draw.rect(surface, (20, 20, 34), rect, 1)
