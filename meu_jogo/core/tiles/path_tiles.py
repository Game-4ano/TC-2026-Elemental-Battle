"""Tiles de caminho conectivo (estrada, madeira, ponte)."""

import pygame

from meu_jogo.core.tiles.base import Tile


class StoneRoadTile(Tile):
    tile_sprite_key = "stone_road"

    def __init__(self):
        super().__init__("Estrada de Pedra", "None", (180, 175, 165), True, 0)

    def draw(self, surface, grid_pos, size, camera_offset):
        rect = self._screen_rect(grid_pos, size, camera_offset)
        pygame.draw.rect(surface, self.color, rect)
        for i in range(2):
            sx2 = rect.x + size // 3 * (i + 1)
            pygame.draw.line(surface, (140, 135, 125), (sx2, rect.y+2), (sx2, rect.y+size-2), 1)
        pygame.draw.rect(surface, (130, 125, 115), rect, 1)


class WoodPathTile(Tile):
    tile_sprite_key = "wood_path"

    def __init__(self):
        super().__init__("Caminho de Madeira", "None", (160, 100, 50), True, 0)

    def draw(self, surface, grid_pos, size, camera_offset):
        rect = self._screen_rect(grid_pos, size, camera_offset)
        pygame.draw.rect(surface, self.color, rect)
        grain = (140, 85, 40)
        for i in range(3):
            gy = rect.y + size // 4 * (i + 1)
            pygame.draw.line(surface, grain, (rect.x+2, gy), (rect.x+size-2, gy), 1)
        pygame.draw.rect(surface, (110, 65, 25), rect, 1)


class WoodBridgeTile(Tile):
    tile_sprite_key = "wood_bridge"

    def __init__(self):
        super().__init__("Ponte de Madeira", "None", (140, 90, 45), True, 0)

    def draw(self, surface, grid_pos, size, camera_offset):
        rect = self._screen_rect(grid_pos, size, camera_offset)
        pygame.draw.rect(surface, (20, 80, 180), rect)
        plank_color = (140, 90, 45)
        for i in range(4):
            py2 = rect.y + size // 4 * i + 2
            plank_r = pygame.Rect(rect.x + 2, py2, size - 4, size // 4 - 2)
            pygame.draw.rect(surface, plank_color, plank_r)
            pygame.draw.rect(surface, (100, 60, 25), plank_r, 1)
