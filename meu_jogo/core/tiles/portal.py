"""PortalTile — leva o jogador a outra sala/mundo ao ser pisado."""

import math

import pygame

from meu_jogo.core.tiles.base import Tile


class PortalTile(Tile):
    def __init__(self, name, color, destination_map_name, spawn_pos: pygame.Vector2):
        super().__init__(name, "None", color, True, 0)
        self.destination_map_name = destination_map_name
        self.spawn_pos = spawn_pos

    def on_step(self, player, map_manager):
        if map_manager:
            map_manager.request_map_change(
                self.destination_map_name, self.spawn_pos
            )

    def draw(self, surface, grid_pos, size, camera_offset):
        rect = self._screen_rect(grid_pos, size, camera_offset)
        dark = tuple(max(c - 60, 0) for c in self.color)
        pygame.draw.rect(surface, dark, rect)

        t  = pygame.time.get_ticks() / 1000.0
        cx, cy = rect.centerx, rect.centery

        # Anéis pulsantes concêntricos
        for ring in range(3, 0, -1):
            phase = math.sin(t * 2.5 + ring * 0.9)
            r = size // 2 - ring * 3 + int(phase * 2)
            if r > 1:
                brightness = 60 + ring * 35
                c_rgb = tuple(min(c + brightness, 255) for c in self.color)
                thick = 2 if ring == 3 else 1
                pygame.draw.circle(surface, c_rgb, (cx, cy), r, thick)

        # 4 partículas rotacionando
        for i in range(4):
            angle = t * 2.5 + i * (math.pi / 2)
            pr = size // 3
            ppx = cx + int(math.cos(angle) * pr)
            ppy = cy + int(math.sin(angle) * pr)
            bright = tuple(min(c + 130, 255) for c in self.color)
            pygame.draw.circle(surface, bright, (ppx, ppy), 2)

        # Anel externo pulsante
        outer_r = size // 2 - 1 + int(abs(math.sin(t * 2.0)) * 3)
        outer_c = tuple(min(c + 50, 255) for c in self.color)
        pygame.draw.circle(surface, outer_c, (cx, cy), outer_r, 1)
        pygame.draw.rect(surface, (210, 210, 210), rect, 1)
