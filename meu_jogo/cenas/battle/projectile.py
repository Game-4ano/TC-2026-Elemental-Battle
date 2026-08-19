"""Projectile — projetil elemental disparado durante os ataques."""

import pygame

from meu_jogo.core.game_object import GameObject
from meu_jogo.core.config import WHITE
from meu_jogo.cenas.battle.constants import ELEMENT_COLORS, _to_rgb


class Projectile(GameObject):
    SPEED  = 340.0
    RADIUS = 10

    def __init__(self, origin, target_obj, element, on_hit_callback):
        super().__init__(origin)
        self.target_obj = target_obj
        self.element    = element
        self.on_hit     = on_hit_callback
        self.color      = ELEMENT_COLORS.get(element, WHITE)
        self._hit       = False
        self._trail: list[pygame.Vector2] = []

        direction = target_obj.position - origin
        if direction.length() > 0:
            self.velocity = direction.normalize() * self.SPEED

    def update(self, dt: float):
        if self._hit:
            return
        self._trail.append(pygame.Vector2(self.position))
        if len(self._trail) > 8:
            self._trail.pop(0)
        self.apply_physics(dt)
        if self.position.distance_to(self.target_obj.position) < 40:
            self._hit  = True
            self.alive = False
            self.on_hit()

    def draw(self, screen: pygame.Surface):
        if self._hit:
            return
        for i, pos in enumerate(self._trail):
            alpha  = int(180 * (i / max(len(self._trail), 1)))
            radius = max(2, int(self.RADIUS * (i / max(len(self._trail), 1))))
            surf   = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            _rgb = _to_rgb(self.color)
            pygame.draw.circle(surf, (_rgb[0], _rgb[1], _rgb[2], alpha), (radius, radius), radius)
            screen.blit(surf, (int(pos.x) - radius, int(pos.y) - radius))
        _rgb = _to_rgb(self.color)
        pygame.draw.circle(screen, _rgb,
            (int(self.position.x), int(self.position.y)), self.RADIUS)
        bright = tuple(min(c + 100, 255) for c in _rgb)
        pygame.draw.circle(screen, bright,
            (int(self.position.x), int(self.position.y)), self.RADIUS - 4)
