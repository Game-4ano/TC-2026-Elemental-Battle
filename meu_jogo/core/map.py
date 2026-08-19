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
        self._camera_offset = pygame.Vector2(0.0, 0.0)
        self.bg_image    = bg_image   # pygame.Surface opcional

    def get_tile_at(self, grid_pos: pygame.Vector2):
        gx, gy = int(grid_pos.x), int(grid_pos.y)
        if 0 <= gy < self.height and 0 <= gx < self.width:
            return self.tile_types.get(self.matrix[gy][gx])
        return None

    def is_walkable(self, grid_pos: pygame.Vector2):
        tile = self.get_tile_at(grid_pos)
        return tile.is_walkable if tile else False

    def update_camera(self, player_pixel: pygame.Vector2, dt=0.016):
        max_x = max(0.0, self.width  * self.tile_size - SCREEN_WIDTH)
        max_y = max(0.0, self.height * self.tile_size - SCREEN_HEIGHT)
        target = pygame.Vector2(
            max(0.0, min(player_pixel.x - SCREEN_WIDTH  // 2, max_x)),
            max(0.0, min(player_pixel.y - SCREEN_HEIGHT // 2, max_y)),
        )
        alpha = min(1.0, 8.0 * dt)
        self._camera_offset += (target - self._camera_offset) * alpha

    def draw(self, surface: pygame.Surface):
        if self.bg_image:
            scaled = pygame.transform.scale(self.bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
            surface.blit(scaled, (0, 0))
        else:
            surface.fill((20, 20, 30))

        # Renderizar só tiles visíveis na câmera
        ts  = self.tile_size
        ox  = int(self._camera_offset.x)
        oy  = int(self._camera_offset.y)
        x0  = max(0, ox // ts)
        y0  = max(0, oy // ts)
        x1  = min(self.width,  x0 + SCREEN_WIDTH  // ts + 2)
        y1  = min(self.height, y0 + SCREEN_HEIGHT // ts + 2)

        for y in range(y0, y1):
            for x in range(x0, x1):
                grid_pos = pygame.Vector2(x, y)
                tile = self.get_tile_at(grid_pos)
                if tile:
                    tile.draw(surface, grid_pos, ts, self._camera_offset)
