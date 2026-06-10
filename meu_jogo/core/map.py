"""
core/map.py — estrutura de mapa baseada em tiles.

As classes de tile foram movidas para o subpacote `core/tiles/` e sao
reexportadas aqui (`from meu_jogo.core.tiles import *`) para preservar os
imports historicos `from meu_jogo.core.map import <AlgumTile>`.
O MapManager mora em `core/map_manager.py`.
"""

import pygame
from meu_jogo.core.config import TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT

# Reexporta todas as classes de tile (compatibilidade de imports antigos).
from meu_jogo.core.tiles import *  # noqa: F401,F403


class Stage:
    def __init__(self, name):
        self.name = name

    def update(self): pass
    def draw(self, surface): pass


# ---------------------------------------------------------------------------
# Map (Stage baseado em tiles) — com suporte a imagem de fundo
# ---------------------------------------------------------------------------
class Map(Stage):
    def __init__(self, name, tile_matrix, tile_types,
                 tile_size=TILE_SIZE, bg_image: pygame.Surface | None = None):
        super().__init__(name)
        self.matrix      = tile_matrix
        self.tile_types  = tile_types
        self.tile_size   = tile_size
        self.width       = len(tile_matrix[0]) if tile_matrix else 0
        self.height      = len(tile_matrix)
        self.camera_offset_x = 0.0
        self.camera_offset_y = 0.0
        self.bg_image    = bg_image   # pygame.Surface opcional

    def get_tile_at(self, grid_x, grid_y):
        if 0 <= grid_y < self.height and 0 <= grid_x < self.width:
            return self.tile_types.get(self.matrix[grid_y][grid_x])
        return None

    def is_walkable(self, grid_x, grid_y):
        tile = self.get_tile_at(grid_x, grid_y)
        return tile.is_walkable if tile else False

    def update_camera(self, player_pixel_x, player_pixel_y, dt=0.016):
        target_x = float(player_pixel_x - SCREEN_WIDTH  // 2)
        target_y = float(player_pixel_y - SCREEN_HEIGHT // 2)
        max_x = max(0.0, self.width  * self.tile_size - SCREEN_WIDTH)
        max_y = max(0.0, self.height * self.tile_size - SCREEN_HEIGHT)
        target_x = max(0.0, min(target_x, max_x))
        target_y = max(0.0, min(target_y, max_y))
        alpha = min(1.0, 8.0 * dt)
        self.camera_offset_x += (target_x - self.camera_offset_x) * alpha
        self.camera_offset_y += (target_y - self.camera_offset_y) * alpha

    def draw(self, surface: pygame.Surface):
        if self.bg_image:
            scaled = pygame.transform.scale(self.bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
            surface.blit(scaled, (0, 0))
        else:
            surface.fill((20, 20, 30))

        # Renderizar só tiles visíveis na câmera
        ts  = self.tile_size
        ox  = int(self.camera_offset_x)
        oy  = int(self.camera_offset_y)
        x0  = max(0, ox // ts)
        y0  = max(0, oy // ts)
        x1  = min(self.width,  x0 + SCREEN_WIDTH  // ts + 2)
        y1  = min(self.height, y0 + SCREEN_HEIGHT // ts + 2)

        for y in range(y0, y1):
            for x in range(x0, x1):
                tile = self.get_tile_at(x, y)
                if tile:
                    tile.draw(surface, x, y, ts,
                              self.camera_offset_x, self.camera_offset_y)


class GameMap:
    """Compatibilidade com a estrutura antiga."""
    def __init__(self, name, enemies, boss):
        self.name    = name
        self.enemies = enemies
        self.boss    = boss
