"""
meu_jogo/midia/sprites/animated_sprite.py

Utilitário reutilizável para animar sprites frame-a-frame.

USO:
    from meu_jogo.midia.sprites.animated_sprite import AnimatedSprite

    # Cria com a chave de animação e escala desejadas
    anim = AnimatedSprite("hero_walk", scale=3, fps=8)

    # No loop principal:
    anim.update(dt)          # avança o timer
    anim.draw(screen, x, y)  # desenha o frame atual

    # Para espelhar horizontalmente (ex: andar para a esquerda):
    anim.flipped = True
"""

import pygame
from meu_jogo.midia.sprites.sprite_factory import get_animation, get_sprite


class AnimatedSprite:
    """
    Gerencia uma sequência de frames e avança entre eles com base no tempo.

    Parâmetros
    ----------
    anim_key  : chave em _ANIMATION_DATA da sprite_factory (ex: "hero_walk")
    scale     : fator de escala aplicado a todos os frames
    fps       : quantos frames por segundo a animação deve rodar
    flipped   : se True, espelha todos os frames horizontalmente
    """

    def __init__(
        self,
        anim_key: str,
        scale: int = 3,
        fps: float = 8.0,
        flipped: bool = False,
    ):
        self.fps     = fps
        self.flipped = flipped
        self._timer  = 0.0
        self._index  = 0

        # Carrega frames da factory (podem vir do cache)
        raw_frames = get_animation(anim_key, scale)

        if not raw_frames:
            # Fallback: tenta carregar como sprite estático
            static = get_sprite(anim_key, scale)
            raw_frames = [static] if static else []

        self._frames         = raw_frames
        self._frames_flipped = [
            pygame.transform.flip(f, True, False) for f in raw_frames
        ]

    # ------------------------------------------------------------------
    def update(self, dt: float):
        """Avança o timer e troca de frame quando necessário."""
        if not self._frames:
            return
        self._timer += dt
        frame_duration = 1.0 / self.fps
        while self._timer >= frame_duration:
            self._timer -= frame_duration
            self._index  = (self._index + 1) % len(self._frames)

    def reset(self):
        """Volta para o primeiro frame (útil ao parar o movimento)."""
        self._index = 0
        self._timer = 0.0

    # ------------------------------------------------------------------
    @property
    def current_frame(self) -> pygame.Surface | None:
        if not self._frames:
            return None
        if self.flipped:
            return self._frames_flipped[self._index]
        return self._frames[self._index]

    @property
    def width(self) -> int:
        return self._frames[0].get_width() if self._frames else 0

    @property
    def height(self) -> int:
        return self._frames[0].get_height() if self._frames else 0

    # ------------------------------------------------------------------
    def draw(self, screen: pygame.Surface, x: int, y: int):
        """Desenha o frame atual em (x, y) — canto superior esquerdo."""
        frame = self.current_frame
        if frame:
            screen.blit(frame, (x, y))