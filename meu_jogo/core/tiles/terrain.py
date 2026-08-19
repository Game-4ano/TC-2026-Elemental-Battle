"""Tiles basicos de terreno (grama, parede, vegetacao do centro)."""

import pygame

from meu_jogo.core.tiles.base import Tile


class GrassTile(Tile):
    tile_sprite_key = "grass"

    def __init__(self, name="Grama", color=(55, 140, 55)):
        super().__init__(name, "Grass", color, True, 0)

    def draw(self, surface, grid_pos, size, camera_offset):
        if self._try_draw_sprite(surface, grid_pos, size, camera_offset):
            return
        rect = self._screen_rect(grid_pos, size, camera_offset)
        pygame.draw.rect(surface, self.color, rect)
        stripe = (max(self.color[0]-15,0), min(self.color[1]+20,255), max(self.color[2]-10,0))
        for i in range(3):
            sx = rect.x + size // 4 * (i + 1)
            pygame.draw.line(surface, stripe, (sx, rect.y+4), (sx, rect.y+size-4), 1)
        pygame.draw.rect(surface, (30, 100, 30), rect, 1)


class WallTile(Tile):
    tile_sprite_key = "rock"

    def __init__(self, name="Montanha", color=(90, 60, 30)):
        super().__init__(name, "None", color, False, 0)

    def draw(self, surface, grid_pos, size, camera_offset):
        if self._try_draw_sprite(surface, grid_pos, size, camera_offset):
            return
        rect = self._screen_rect(grid_pos, size, camera_offset)
        pygame.draw.rect(surface, self.color, rect)
        top_color = (min(self.color[0]+30,255), min(self.color[1]+20,255), min(self.color[2]+10,255))
        top_rect  = pygame.Rect(rect.x, rect.y, rect.w, rect.h // 3)
        pygame.draw.rect(surface, top_color, top_rect)
        pygame.draw.rect(surface, (40, 25, 10), rect, 1)


class FlowerGrassTile(Tile):
    tile_sprite_key = "flower_grass"

    def __init__(self):
        super().__init__("Grama Florida", "Grass", (60, 150, 60), True, 0)

    def draw(self, surface, grid_pos, size, camera_offset):
        if self._try_draw_sprite(surface, grid_pos, size, camera_offset):
            return
        rect = self._screen_rect(grid_pos, size, camera_offset)
        pygame.draw.rect(surface, self.color, rect)
        stripe = (40, 120, 40)
        for i in range(3):
            sx2 = rect.x + size // 4 * (i + 1)
            pygame.draw.line(surface, stripe, (sx2, rect.y+4), (sx2, rect.y+size-4), 1)
        colors = [(255, 80, 80), (255, 220, 50), (150, 100, 255)]
        gx, gy = int(grid_pos.x), int(grid_pos.y)
        for i in range(2):
            fx = rect.x + (i * 11 + gx * 7) % (size - 6) + 3
            fy = rect.y + (i * 8 + gy * 5) % (size - 6) + 3
            pygame.draw.circle(surface, colors[(gx + gy + i) % 3], (fx, fy), 2)
        pygame.draw.rect(surface, (30, 100, 30), rect, 1)


class BushTile(Tile):
    tile_sprite_key = "bush"

    def __init__(self):
        super().__init__("Arbusto", "Grass", (30, 100, 30), False, 0)

    def draw(self, surface, grid_pos, size, camera_offset):
        if self._try_draw_sprite(surface, grid_pos, size, camera_offset):
            return
        rect = self._screen_rect(grid_pos, size, camera_offset)
        pygame.draw.rect(surface, (40, 80, 20), rect)
        for ox, oy, r in [(-4, 0, 7), (4, -2, 6), (0, 4, 6), (-3, -3, 5)]:
            cx2 = rect.centerx + ox
            cy2 = rect.centery + oy
            if rect.collidepoint(cx2, cy2):
                pygame.draw.circle(surface, (50, 140, 30), (cx2, cy2), r)
        pygame.draw.rect(surface, (20, 60, 10), rect, 1)


class TreeTile(Tile):
    tile_sprite_key = "tree"

    def __init__(self):
        super().__init__("Árvore", "Grass", (30, 80, 20), False, 0)

    def draw(self, surface, grid_pos, size, camera_offset):
        if self._try_draw_sprite(surface, grid_pos, size, camera_offset):
            return
        rect = self._screen_rect(grid_pos, size, camera_offset)
        pygame.draw.rect(surface, (20, 60, 10), rect)
        trunk_r = pygame.Rect(rect.centerx - 3, rect.centery, 6, size // 2)
        pygame.draw.rect(surface, (100, 60, 20), trunk_r)
        pygame.draw.circle(surface, (40, 140, 30), (rect.centerx, rect.centery - 2), size // 3)
        pygame.draw.circle(surface, (60, 170, 40), (rect.centerx - 3, rect.centery - 4), size // 5)
        pygame.draw.circle(surface, (35, 120, 25), (rect.centerx + 3, rect.centery - 3), size // 5)
        pygame.draw.rect(surface, (10, 40, 5), rect, 1)
