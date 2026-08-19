"""Tiles da regiao Agua (Oeste) e decorativos da sala da Hydra."""

import math

import pygame

from meu_jogo.core.tiles.base import Tile


class WaterTile(Tile):
    tile_sprite_key = "water"
    tile_sprite_fps = 1.5

    def __init__(self, name="Poça", color=(30, 100, 200), damage=5):
        super().__init__(name, "Water", color, True, damage)

    def on_step(self, player, map_manager=None):
        dmg = self.damage_on_step * (2 if getattr(player, "element", "") == "Fire" else 1)
        player.take_damage(dmg)

    def draw(self, surface, grid_pos, size, camera_offset):
        if self._try_draw_sprite(surface, grid_pos, size, camera_offset):
            return
        rect = self._screen_rect(grid_pos, size, camera_offset)
        pygame.draw.rect(surface, self.color, rect)
        lighter = (min(self.color[0]+40,255), min(self.color[1]+40,255), min(self.color[2]+50,255))
        wave_y  = rect.y + size // 3
        pygame.draw.line(surface, lighter, (rect.x+3, wave_y), (rect.x + size//2, wave_y), 1)
        pygame.draw.rect(surface, (0, 60, 140), rect, 1)


class IceTile(Tile):
    def __init__(self):
        super().__init__("Gelo", "Water", (180, 220, 240), True, 0)

    def draw(self, surface, grid_pos, size, camera_offset):
        rect = self._screen_rect(grid_pos, size, camera_offset)
        gx, gy = int(grid_pos.x), int(grid_pos.y)
        pygame.draw.rect(surface, self.color, rect)
        t = (pygame.time.get_ticks() % 2000) / 2000.0
        brilho = int(200 + 55 * math.sin(t * 6.28 + gx * 0.7 + gy * 0.5))
        pygame.draw.line(surface, (brilho, brilho, 255), (rect.x+3, rect.y+3), (rect.x+size-3, rect.y+size-3), 1)
        pygame.draw.line(surface, (brilho, brilho, 255), (rect.x+size-3, rect.y+3), (rect.x+3, rect.y+size-3), 1)
        pygame.draw.rect(surface, (120, 180, 220), rect, 1)


class CrystalTile(Tile):
    def __init__(self):
        super().__init__("Cristal Azul", "Water", (40, 80, 180), False, 0)

    def draw(self, surface, grid_pos, size, camera_offset):
        rect = self._screen_rect(grid_pos, size, camera_offset)
        gx, gy = int(grid_pos.x), int(grid_pos.y)
        pygame.draw.rect(surface, (20, 50, 120), rect)
        t = (pygame.time.get_ticks() % 1500) / 1500.0
        glow = int(80 + 120 * abs(math.sin(t * 3.14 + gx + gy)))
        cx, cy = rect.centerx, rect.centery
        pts = [(cx, rect.y+2), (rect.x+size-4, cy), (cx, rect.y+size-2), (rect.x+4, cy)]
        pygame.draw.polygon(surface, (glow, glow, 255), pts)
        pygame.draw.polygon(surface, (180, 220, 255), pts, 1)


class RiverTile(Tile):
    def __init__(self):
        super().__init__("Rio", "Water", (30, 100, 200), True, 3)

    def draw(self, surface, grid_pos, size, camera_offset):
        rect = self._screen_rect(grid_pos, size, camera_offset)
        gx = int(grid_pos.x)
        pygame.draw.rect(surface, (20, 80, 180), rect)
        t = (pygame.time.get_ticks() % 1000) / 1000.0
        shift = int((t + gx * 0.3) * size) % size
        for i in range(3):
            wy = rect.y + size // 4 * (i + 1)
            wx = rect.x + (shift + i * 5) % (size - 4)
            lighter = (60, 160, 255)
            pygame.draw.line(surface, lighter, (wx, wy), (wx + size // 3, wy), 2)
        pygame.draw.rect(surface, (0, 50, 140), rect, 1)


class WetSandTile(Tile):
    def __init__(self):
        super().__init__("Areia Úmida", "Water", (100, 120, 100), True, 0)

    def draw(self, surface, grid_pos, size, camera_offset):
        rect = self._screen_rect(grid_pos, size, camera_offset)
        gx, gy = int(grid_pos.x), int(grid_pos.y)
        pygame.draw.rect(surface, self.color, rect)
        for i in range(4):
            px2 = rect.x + (i * 7 + gx * 3) % (size - 4)
            py2 = rect.y + (i * 5 + gy * 3) % (size - 4)
            pygame.draw.circle(surface, (70, 100, 80), (px2, py2), 1)
        pygame.draw.rect(surface, (60, 90, 70), rect, 1)


class DeepWaterTile(Tile):
    def __init__(self):
        super().__init__("Água Profunda", "Water", (10, 40, 130), False, 0)

    def draw(self, surface, grid_pos, size, camera_offset):
        rect = self._screen_rect(grid_pos, size, camera_offset)
        gx = int(grid_pos.x)
        pygame.draw.rect(surface, self.color, rect)
        t = pygame.time.get_ticks() / 1000.0
        for i in range(2):
            wy = rect.y + size // 3 * (i + 1)
            shift = int(math.sin(t * 1.5 + i + gx * 0.5) * 4)
            pygame.draw.line(surface, (30, 80, 180),
                             (rect.x + 2 + shift, wy),
                             (rect.x + size - 2 + shift, wy), 1)
        pygame.draw.rect(surface, (5, 20, 80), rect, 1)


class IceStalactiteTile(Tile):
    def __init__(self):
        super().__init__("Estalactite de Gelo", "Water", (140, 200, 230), False, 0)

    def draw(self, surface, grid_pos, size, camera_offset):
        rect = self._screen_rect(grid_pos, size, camera_offset)
        gx = int(grid_pos.x)
        pygame.draw.rect(surface, (100, 160, 200), rect)
        t = pygame.time.get_ticks() / 1000.0
        for i in range(3):
            tip_x  = rect.x + size // 4 * (i + 1)
            height = size // 2 + int(4 * abs(math.sin(t * 0.5 + i + gx)))
            pts    = [(tip_x - 4, rect.y + 2), (tip_x + 4, rect.y + 2),
                      (tip_x, rect.y + height)]
            pygame.draw.polygon(surface, (190, 230, 255), pts)
            pygame.draw.polygon(surface, (140, 200, 240), pts, 1)
        pygame.draw.rect(surface, (80, 140, 190), rect, 1)


class BubbleTile(Tile):
    def __init__(self):
        super().__init__("Bolhas", "Water", (20, 80, 180), True, 0)

    def draw(self, surface, grid_pos, size, camera_offset):
        rect = self._screen_rect(grid_pos, size, camera_offset)
        gx = int(grid_pos.x)
        pygame.draw.rect(surface, (15, 60, 150), rect)
        t = pygame.time.get_ticks() / 1000.0
        for i in range(3):
            phase  = (t * 0.8 + i * 0.7 + gx * 0.3) % 1.0
            bx2    = rect.x + (i * 9 + gx * 5) % (size - 6) + 3
            by2    = rect.y + size - int(phase * size)
            r      = int(2 + 2 * abs(math.sin(t * 1.2 + i)))
            alpha2 = int(180 * (1 - phase))
            s      = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (100, 180, 255, alpha2), (r, r), r)
            pygame.draw.circle(s, (200, 240, 255, alpha2 // 2), (r, r), r, 1)
            surface.blit(s, (bx2 - r, by2 - r))
        pygame.draw.rect(surface, (10, 40, 120), rect, 1)


class MushroomTile(Tile):
    def __init__(self):
        super().__init__("Cogumelo", "Water", (30, 80, 30), True, 0)

    def draw(self, surface, grid_pos, size, camera_offset):
        rect = self._screen_rect(grid_pos, size, camera_offset)
        gx = int(grid_pos.x)
        pygame.draw.rect(surface, (30, 75, 30), rect)
        t = pygame.time.get_ticks() / 1000.0
        cx, cy = rect.centerx, rect.centery
        # Talo
        pygame.draw.rect(surface, (210, 190, 170), (cx - 2, cy, 4, size // 3))
        # Cabeça animada (oscila levemente e pulsa de cor)
        sway = int(1.5 * math.sin(t * 1.2 + gx * 0.7))
        cap_r = int(185 + 50 * abs(math.sin(t * 0.9 + gx * 0.5)))
        pygame.draw.ellipse(surface, (cap_r, 40, 40),
                            (cx - 6 + sway, cy - size // 4, 12, 8))
        pygame.draw.ellipse(surface, (255, 120, 100),
                            (cx - 6 + sway, cy - size // 4, 12, 8), 1)
        pygame.draw.rect(surface, (20, 55, 20), rect, 1)
