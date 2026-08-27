"""
CharacterObject — representacao visual de um personagem na tela de batalha:
sprite animado (via AnimationController) + barra de HP, com fallback de
retangulo colorido quando nao ha sprite.
"""

import random

import pygame

from meu_jogo.core.game_object import GameObject
from meu_jogo.core.config import WHITE
from meu_jogo.core.elements import ELEMENT_NAMES_PT
from meu_jogo.midia.sprites.sprite_factory import get_sprite
from meu_jogo.midia.sprites.animated_sprite import AnimationController
from meu_jogo.cenas.battle.constants import ELEMENT_COLORS

# Escala do sprite na tela de batalha.
# 16x16 x 5 = 80x80 px
_SPRITE_SCALE = 5


class CharacterObject(GameObject):
    """
    Representa visualmente um personagem na tela de batalha.
    Suporta animacoes de idle, ataque, dano e morte via AnimatedSprite.
    Fallback: retangulo colorido se sprite_key nao existir.
    """

    SIZE = 16 * _SPRITE_SCALE   # 80 px

    # Estados de animacao
    IDLE   = "idle"
    ATTACK = "attack"
    HURT   = "hurt"
    DYING  = "dying"

    def __init__(self, character, position, fallback_color, facing_right):
        super().__init__(position)
        self.character      = character
        self.fallback_color = fallback_color
        self.facing_right   = facing_right
        self._shake_timer   = 0.0
        self._shake_off     = pygame.Vector2(0, 0)
        self._flash_timer   = 0.0
        self._flash_color   = (255, 255, 255)

        # HP animado: interpola suavemente em direcao ao HP real
        self._hp_display: float = float(character.hp)

        # Sprite estático (fallback quando AnimationController não tem frames)
        self._sprite: pygame.Surface | None = self._load_sprite()
        self._sprite_flipped: pygame.Surface | None = (
            pygame.transform.flip(self._sprite, True, False)
            if self._sprite and not facing_right else None
        )

        skey = getattr(character, "sprite_key", "") or ""
        if facing_right:
            states = {
                "idle":   {"anim_key": "hero_idle_breath", "fps": 1.8,  "loop": True},
                "attack": {"anim_key": "hero_attack",       "fps": 8.0,  "loop": False},
                "hurt":   {"anim_key": "hero_hurt",         "fps": 6.0,  "loop": False},
                "dying":  {"anim_key": "hero_idle_breath",  "fps": 1.8,  "loop": False},
            }
        else:
            states = {
                "idle":   {"anim_key": f"{skey}_idle",   "fps": 1.8,  "loop": True},
                "attack": {"anim_key": f"{skey}_attack", "fps": 8.0,  "loop": False},
                "hurt":   {"anim_key": f"{skey}_hurt",   "fps": 6.0,  "loop": False},
                "dying":  {"anim_key": f"{skey}_death",  "fps": 3.5,  "loop": False},
            }
        self._ctrl = AnimationController(
            states, scale=_SPRITE_SCALE, flipped=not facing_right)

        self._state          = self.IDLE
        self._state_timer    = 0.0
        self._state_duration = 0.0

    # ── Carregamento ──────────────────────────────────────────────────────────

    def _load_sprite(self) -> pygame.Surface | None:
        key = getattr(self.character, "sprite_key", None)
        if not key:
            return None
        return get_sprite(key, scale=_SPRITE_SCALE)

    # ── Triggers de estado ────────────────────────────────────────────────────

    def play_attack(self):
        """Inicia animacao de ataque (0.35s, nao-loop)."""
        self._ctrl.play("attack", force_restart=True)
        self._state          = self.ATTACK
        self._state_timer    = 0.0
        self._state_duration = 0.35

    def take_hit(self, flash_color=(255, 255, 255)):
        """Flash + shake + animacao de hurt."""
        self._shake_timer = 0.3
        self._flash_timer = 0.2
        self._flash_color = flash_color
        self._ctrl.play("hurt", force_restart=True)
        self._state          = self.HURT
        self._state_timer    = 0.0
        self._state_duration = 0.3

    def start_death_anim(self):
        """Inicia dissolucao (0.9s)."""
        self._ctrl.play("dying", force_restart=True)
        self._state          = self.DYING
        self._state_timer    = 0.0
        self._state_duration = 0.9

    @property
    def death_anim_done(self) -> bool:
        return self._state == self.DYING and self._state_timer >= self._state_duration

    # ── Update ────────────────────────────────────────────────────────────────

    def update(self, dt: float):
        if self._shake_timer > 0:
            self._shake_timer -= dt
            self._shake_off = pygame.Vector2(
                random.uniform(-5, 5), random.uniform(-3, 3))
        else:
            self._shake_off = pygame.Vector2(0, 0)
        if self._flash_timer > 0:
            self._flash_timer -= dt

        target = float(max(self.character.hp, 0))
        diff   = target - self._hp_display
        if abs(diff) > 0.5:
            self._hp_display += diff * min(7.0 * dt, 1.0)
        else:
            self._hp_display = target

        if self._state != self.IDLE:
            self._state_timer += dt
            if self._state != self.DYING and self._state_timer >= self._state_duration:
                self._state = self.IDLE
                self._ctrl.play("idle")

        self._ctrl.update(dt)

    # ── Draw ──────────────────────────────────────────────────────────────────

    def _current_surf(self) -> pygame.Surface | None:
        frame = self._ctrl.current_frame
        if frame:
            return frame
        return self._sprite_flipped if self._sprite_flipped else self._sprite

    def draw(self, screen: pygame.Surface):
        dp = self.position + self._shake_off
        cx, cy = int(dp.x), int(dp.y)

        dying    = self._state == self.DYING
        progress = (self._state_timer / max(self._state_duration, 0.01)) if dying else 0.0

        # Sombra (desaparece durante morte)
        if not dying or progress < 0.7:
            pygame.draw.ellipse(screen, (0, 0, 0),
                (cx + 6, cy + self.SIZE - 6, self.SIZE - 12, 10))

        surf = self._current_surf()

        if surf:
            if dying:
                surf = surf.copy()
                surf.set_alpha(max(0, int(255 * (1.0 - progress))))
            elif self._flash_timer > 0:
                surf = surf.copy()
                surf.fill((*self._flash_color, 160), special_flags=pygame.BLEND_RGBA_MULT)
            screen.blit(surf, (cx, cy))

            if not dying:
                elem_c = ELEMENT_COLORS.get(self.character.element, WHITE)
                pygame.draw.rect(screen, elem_c,
                    (cx - 2, cy - 2, self.SIZE + 4, self.SIZE + 4), 2)
        else:
            color = (255, 255, 255) if self._flash_timer > 0 else self.fallback_color
            body  = pygame.Rect(cx, cy, self.SIZE, self.SIZE)
            pygame.draw.rect(screen, color, body, border_radius=14)
            elem_c = ELEMENT_COLORS.get(self.character.element, WHITE)
            pygame.draw.rect(screen, elem_c, body, 3, border_radius=14)

        if not dying:
            font = pygame.font.SysFont(None, 19)
            elem_c = ELEMENT_COLORS.get(self.character.element, WHITE)
            lbl = font.render(
                f"[{ELEMENT_NAMES_PT.get(self.character.element, self.character.element)}]",
                True, elem_c)
            screen.blit(lbl, (cx, cy + self.SIZE + 2))
            if self.character.is_boss:
                tag = pygame.font.SysFont(None, 20).render("BOSS", True, (220, 180, 0))
                screen.blit(tag, (cx, cy - 18))

    def draw_hud(self, screen, hud_pos: pygame.Vector2):
        hud_x, hud_y = int(hud_pos.x), int(hud_pos.y)
        font   = pygame.font.SysFont(None, 22)
        bfont  = pygame.font.SysFont(None, 23)
        sfont  = pygame.font.SysFont(None, 17)
        elem_c = ELEMENT_COLORS.get(self.character.element, WHITE)

        panel = pygame.Rect(hud_x, hud_y, 180, 64)
        bg    = pygame.Surface((panel.w, panel.h), pygame.SRCALPHA)
        bg.fill((8, 6, 18, 215))
        screen.blit(bg, panel.topleft)
        pygame.draw.rect(screen, elem_c, panel, 2, border_radius=6)
        pygame.draw.rect(screen, tuple(max(0, c - 80) for c in elem_c),
                         panel.inflate(-5, -5), 1, border_radius=4)

        pygame.draw.circle(screen, elem_c, (hud_x + 13, hud_y + 13), 8)
        pygame.draw.circle(screen, WHITE,  (hud_x + 13, hud_y + 13), 8, 1)

        name_s = bfont.render(
            f"{self.character.name}  Lv.{self.character.level}", True, WHITE)
        screen.blit(name_s, (hud_x + 26, hud_y + 5))

        if self.character.is_boss:
            # Canto inferior direito do painel — livre (barra de HP e nome do
            # elemento ocupam só a metade esquerda), sem colidir com o nome.
            tbg = pygame.Surface((40, 14), pygame.SRCALPHA)
            tbg.fill((140, 90, 0, 220))
            screen.blit(tbg, (panel.right - 46, hud_y + 46))
            screen.blit(sfont.render("BOSS", True, (255, 215, 0)),
                        (panel.right - 44, hud_y + 47))

        bar_w, bar_h = 160, 12
        bx, by = hud_x + 10, hud_y + 28
        ratio  = max(self._hp_display, 0) / max(self.character.max_hp, 1)
        filled = int(bar_w * ratio)
        pygame.draw.rect(screen, (40, 12, 12), (bx, by, bar_w, bar_h), border_radius=5)
        if filled > 0:
            hp_c = ((60, 200, 60) if ratio > 0.5 else
                    (220, 180, 0) if ratio > 0.25 else (220, 40, 40))
            pygame.draw.rect(screen, hp_c, (bx, by, filled, bar_h), border_radius=5)
        pygame.draw.rect(screen, (130, 130, 130), (bx, by, bar_w, bar_h), 1, border_radius=5)
        screen.blit(font.render(
            f"{max(0, int(self._hp_display))}/{self.character.max_hp}", True, WHITE),
            (bx + 2, by - 1))

        screen.blit(sfont.render(
            ELEMENT_NAMES_PT.get(self.character.element, self.character.element),
            True, elem_c), (hud_x + 26, hud_y + 46))
