"""Tiles da regiao Fogo (Leste) e decorativos da sala do Magma Titan."""

import math

import pygame

from meu_jogo.core.tiles.base import Tile


class FireTile(Tile):
    def __init__(self, name="Brasa", color=(200, 60, 0), damage=10):
        super().__init__(name, "Fire", color, True, damage)

    def on_step(self, player, map_manager=None):
        dmg = self.damage_on_step * (2 if getattr(player, "element", "") == "Grass" else 1)
        player.take_damage(dmg)

    def draw(self, surface, x, y, size, offset_x=0, offset_y=0):
        rect = pygame.Rect(x * size - offset_x, y * size - offset_y, size, size)
        pygame.draw.rect(surface, self.color, rect)
        # Brilho no centro
        cx, cy = rect.centerx, rect.centery
        pygame.draw.circle(surface, (240, 140, 0), (cx, cy), size // 5)
        pygame.draw.rect(surface, (140, 30, 0), rect, 1)


class LavaTile(Tile):
    def __init__(self):
        super().__init__("Lava", "Fire", (200, 50, 0), True, 8)

    def on_step(self, player, map_manager=None):
        dmg = self.damage_on_step * (2 if getattr(player, "element", "") == "Grass" else 1)
        player.take_damage(dmg)

    def draw(self, surface, x, y, size, offset_x=0, offset_y=0):
        rect = pygame.Rect(x * size - offset_x, y * size - offset_y, size, size)
        pygame.draw.rect(surface, (180, 40, 0), rect)
        t = pygame.time.get_ticks() / 1000.0
        for i in range(3):
            bx = rect.x + size // 4 * (i + 1)
            phase = math.sin(t * 2.5 + i * 1.2 + x * 0.4 + y * 0.3)
            by = rect.centery + int(phase * size // 5)
            r = int(3 + 2 * abs(phase))
            pygame.draw.circle(surface, (255, 160 + int(60 * abs(phase)), 0), (bx, by), r)
        pygame.draw.rect(surface, (120, 20, 0), rect, 1)


class HotRockTile(Tile):
    tile_sprite_key = "hot_rock"

    def __init__(self):
        super().__init__("Rocha Vulcânica", "Fire", (50, 30, 20), True, 0)

    def draw(self, surface, x, y, size, offset_x=0, offset_y=0):
        rect = pygame.Rect(x * size - offset_x, y * size - offset_y, size, size)
        pygame.draw.rect(surface, self.color, rect)
        t = pygame.time.get_ticks() / 1000.0
        for i in range(3):
            cx2 = rect.x + (i * 9 + x * 5) % (size - 6) + 3
            cy2 = rect.y + (i * 7 + y * 4) % (size - 6) + 3
            glow = int(100 + 100 * abs(math.sin(t * 1.5 + i + x * 0.2)))
            pygame.draw.line(surface, (glow, glow // 3, 0),
                             (cx2, cy2), (cx2 + 4, cy2 + 2), 1)
        pygame.draw.rect(surface, (30, 15, 5), rect, 1)


class AshTile(Tile):
    tile_sprite_key = "ash"

    def __init__(self):
        super().__init__("Cinza", "Fire", (140, 130, 120), True, 0)

    def draw(self, surface, x, y, size, offset_x=0, offset_y=0):
        rect = pygame.Rect(x * size - offset_x, y * size - offset_y, size, size)
        pygame.draw.rect(surface, self.color, rect)
        for i in range(6):
            px2 = rect.x + (i * 5 + x * 3) % (size - 2)
            py2 = rect.y + (i * 4 + y * 5) % (size - 2)
            pygame.draw.circle(surface, (80, 70, 65), (px2, py2), 1)
        pygame.draw.rect(surface, (100, 90, 80), rect, 1)


class EmberTile(Tile):
    def __init__(self):
        super().__init__("Brasa", "Fire", (100, 40, 10), True, 2)

    def draw(self, surface, x, y, size, offset_x=0, offset_y=0):
        rect = pygame.Rect(x * size - offset_x, y * size - offset_y, size, size)
        pygame.draw.rect(surface, self.color, rect)
        t = pygame.time.get_ticks() / 1000.0
        for i in range(4):
            bx = rect.x + (i * 7 + x * 4) % (size - 4) + 2
            by = rect.y + (i * 5 + y * 3) % (size - 4) + 2
            pulse = abs(math.sin(t * 3.0 + i + x * 0.5))
            c = int(180 + 75 * pulse)
            pygame.draw.circle(surface, (c, c // 4, 0), (bx, by), 1)
        pygame.draw.rect(surface, (70, 20, 0), rect, 1)


class LavaDropTile(Tile):
    def __init__(self):
        super().__init__("Pingo de Lava", "Fire", (80, 20, 5), True, 2)

    def draw(self, surface, x, y, size, offset_x=0, offset_y=0):
        rect = pygame.Rect(x * size - offset_x, y * size - offset_y, size, size)
        pygame.draw.rect(surface, (55, 15, 3), rect)
        t = pygame.time.get_ticks() / 1000.0
        for i in range(2):
            phase  = (t * 1.2 + i * 0.6 + y * 0.4) % 1.0
            dx2    = (i * 11 + x * 7) % (size - 8) + 4
            dy2    = int(phase * (size - 4))
            cv     = int(200 + 55 * abs(math.sin(t * 3 + i)))
            s      = pygame.Surface((6, 8), pygame.SRCALPHA)
            pts    = [(3, 0), (6, 5), (3, 8), (0, 5)]
            pygame.draw.polygon(s, (cv, cv // 3, 0, 200), pts)
            surface.blit(s, (rect.x + dx2 - 3, rect.y + dy2 - 4))
        pygame.draw.rect(surface, (40, 8, 0), rect, 1)
