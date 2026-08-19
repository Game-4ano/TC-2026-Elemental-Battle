"""Tiles de chao das arenas de batalha (gelo, vulcao, celeste, metalica)."""

import math

import pygame

from meu_jogo.core.tiles.base import Tile


class IceArenaTile(Tile):
    def __init__(self):
        super().__init__("Arena de Gelo", "Water", (160, 210, 240), True, 0)

    def draw(self, surface, grid_pos, size, camera_offset):
        rect = self._screen_rect(grid_pos, size, camera_offset)
        pygame.draw.rect(surface, self.color, rect)
        t = pygame.time.get_ticks() / 1000.0
        gx, gy = int(grid_pos.x), int(grid_pos.y)
        alpha = int(30 + 20 * math.sin(t * 1.5 + gx * 0.6 + gy * 0.4))
        pygame.draw.rect(surface, (200, 240, 255), rect.inflate(-alpha // 3, -alpha // 3), 1)
        # Reflexo deslizante azul-claro
        phase = (t * 0.4 + gx * 0.12 + gy * 0.07) % 1.0
        if phase < 0.3:
            a = int(70 * (1.0 - phase / 0.3))
            rs = pygame.Surface((size, 2), pygame.SRCALPHA)
            rs.fill((200, 235, 255, a))
            surface.blit(rs, (rect.x, rect.y + int(phase / 0.3 * size)))
        pygame.draw.rect(surface, (100, 170, 210), rect, 1)


class VolcanoFloorTile(Tile):
    def __init__(self):
        super().__init__("Chão Vulcânico", "Fire", (40, 25, 15), True, 0)

    def draw(self, surface, grid_pos, size, camera_offset):
        rect = self._screen_rect(grid_pos, size, camera_offset)
        pygame.draw.rect(surface, self.color, rect)
        t = pygame.time.get_ticks() / 1000.0
        gx, gy = int(grid_pos.x), int(grid_pos.y)
        for i in range(3):
            cx2 = rect.x + (i * 8 + gx * 5) % (size - 4) + 2
            cy2 = rect.y + (i * 6 + gy * 4) % (size - 4) + 2
            glow = int(80 + 80 * abs(math.sin(t * 2.0 + i + gx * 0.3)))
            pygame.draw.line(surface, (glow, glow // 3, 0), (cx2, cy2), (cx2 + 5, cy2 + 3), 1)
        # Overlay de calor pulsante laranja
        heat = int(22 + 20 * abs(math.sin(t * 1.8 + gx * 0.2 + gy * 0.3)))
        hs = pygame.Surface((size, size), pygame.SRCALPHA)
        hs.fill((210, 80, 0, heat))
        surface.blit(hs, rect.topleft)
        pygame.draw.rect(surface, (20, 10, 5), rect, 1)


class SkyArenaTile(Tile):
    def __init__(self):
        super().__init__("Arena Celeste", "Air", (195, 215, 240), True, 0)

    def draw(self, surface, grid_pos, size, camera_offset):
        rect = self._screen_rect(grid_pos, size, camera_offset)
        pygame.draw.rect(surface, self.color, rect)
        t = pygame.time.get_ticks() / 1000.0
        gx, gy = int(grid_pos.x), int(grid_pos.y)
        glow = int(200 + 55 * abs(math.sin(t * 0.8 + gx * 0.4)))
        pygame.draw.rect(surface, (glow, glow, 255), rect.inflate(-6, -6), 2)
        # Névoa de nuvem passando horizontalmente
        wisp_phase = (t * 0.5 + gx * 0.18 + gy * 0.09) % 1.0
        if wisp_phase < 0.35:
            wa = int(30 * (1.0 - wisp_phase / 0.35))
            ws = pygame.Surface((size, 3), pygame.SRCALPHA)
            ws.fill((245, 248, 255, wa))
            surface.blit(ws, (rect.x, rect.y + size // 3))
        pygame.draw.rect(surface, (140, 170, 210), rect, 1)


class ForestArenaTile(Tile):
    def __init__(self):
        super().__init__("Arena Ancestral", "Grass", (30, 70, 25), True, 0)

    def draw(self, surface, grid_pos, size, camera_offset):
        rect = self._screen_rect(grid_pos, size, camera_offset)
        pygame.draw.rect(surface, self.color, rect)
        t = pygame.time.get_ticks() / 1000.0
        gx, gy = int(grid_pos.x), int(grid_pos.y)
        glow = int(60 + 40 * abs(math.sin(t * 1.4 + gx * 0.4 + gy * 0.3)))
        pygame.draw.circle(surface, (60, glow + 90, 50), rect.center, size // 5, 1)
        # Vinha pulsando na borda inferior
        vine_phase = (t * 0.5 + gx * 0.2 + gy * 0.15) % 1.0
        if vine_phase < 0.3:
            va = int(70 * (1.0 - vine_phase / 0.3))
            vs = pygame.Surface((size, 2), pygame.SRCALPHA)
            vs.fill((90, 200, 90, va))
            surface.blit(vs, (rect.x, rect.y + size - 3))
        pygame.draw.rect(surface, (18, 45, 15), rect, 1)


class MetalArenaTile(Tile):
    def __init__(self):
        super().__init__("Arena Metálica", "Electric", (120, 130, 150), True, 0)

    def draw(self, surface, grid_pos, size, camera_offset):
        rect = self._screen_rect(grid_pos, size, camera_offset)
        pygame.draw.rect(surface, self.color, rect)
        t = pygame.time.get_ticks() / 1000.0
        gx, gy = int(grid_pos.x), int(grid_pos.y)
        glow = int(50 + 50 * abs(math.sin(t * 2.0 + gx * 0.5 + gy * 0.3)))
        pygame.draw.rect(surface, (80, 100, 130 + glow // 3), rect.inflate(-4, -4), 1)
        cx2, cy2 = rect.centerx, rect.centery
        hs = size // 4
        pts = [(cx2, cy2 - hs), (cx2 + hs, cy2), (cx2, cy2 + hs), (cx2 - hs, cy2)]
        pygame.draw.polygon(surface, (150, 160, 180), pts, 1)
        # Raio horizontal: todos os tiles do mesmo y piscam juntos (~a cada 3.5s)
        active_row = int(t / 3.5) % 8 + 1
        in_flash   = (t % 3.5) < 0.08
        if gy == active_row and in_flash:
            fs = pygame.Surface((size, 2), pygame.SRCALPHA)
            fs.fill((220, 235, 255, 200))
            surface.blit(fs, (rect.x, rect.centery - 1))
        pygame.draw.rect(surface, (80, 90, 110), rect, 1)
