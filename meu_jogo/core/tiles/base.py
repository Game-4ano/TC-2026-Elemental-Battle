"""
Tile base — classe raiz de todos os tiles do mundo e das salas.

Subclasses com pixel art definem `tile_sprite_key`; o desenho real vem de
midia/sprites/tile_sprites.py. Sem sprite registrado, cai no fallback por
primitivas (`draw`).
"""

import pygame


class Tile:
    # Subclasses que possuem pixel art em tile_sprites.py definem esta chave.
    # None = sem sprite, usa draw por primitivas como fallback.
    tile_sprite_key: str | None = None
    tile_sprite_fps: float = 2.0   # frames por segundo para tiles animados

    def __init__(self, name, element, color, is_walkable, damage_on_step=0):
        self.name           = name
        self.element        = element
        self.color          = color
        self.is_walkable    = is_walkable
        self.damage_on_step = damage_on_step

    def on_step(self, player, map_manager=None):
        if self.damage_on_step > 0:
            player.take_damage(self.damage_on_step)

    def _try_draw_sprite(self, surface, x, y, size, offset_x, offset_y) -> bool:
        """Tenta desenhar sprite pixel art. Retorna True se sucesso."""
        if not self.tile_sprite_key:
            return False
        try:
            from meu_jogo.midia.sprites.tile_sprites import get_tile_sprite, get_tile_frame_count
            n = get_tile_frame_count(self.tile_sprite_key)
            if n == 0:
                return False
            frame = int(pygame.time.get_ticks() / (1000.0 / self.tile_sprite_fps)) % n
            spr = get_tile_sprite(self.tile_sprite_key, frame)
            if spr is None:
                return False
            rx = x * size - int(offset_x)
            ry = y * size - int(offset_y)
            if spr.get_width() != size or spr.get_height() != size:
                spr = pygame.transform.scale(spr, (size, size))
            surface.blit(spr, (rx, ry))
            return True
        except Exception:
            return False

    def draw(self, surface, x, y, size, offset_x=0, offset_y=0):
        if self._try_draw_sprite(surface, x, y, size, offset_x, offset_y):
            return
        rect = pygame.Rect(x * size - int(offset_x), y * size - int(offset_y), size, size)
        pygame.draw.rect(surface, self.color, rect)
        border = tuple(max(c - 30, 0) for c in self.color)
        pygame.draw.rect(surface, border, rect, 1)
