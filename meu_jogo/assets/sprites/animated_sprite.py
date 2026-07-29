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
from meu_jogo.assets.sprites.sprite_factory import get_animation, get_sprite


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
        loop: bool = True,
    ):
        self.fps     = fps
        self.flipped = flipped
        self.loop    = loop
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
            if self.loop:
                self._index = (self._index + 1) % len(self._frames)
            else:
                self._index = min(self._index + 1, len(self._frames) - 1)

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


# ─────────────────────────────────────────────────────────────────────────────
#  AnimationController — gerencia múltiplos estados de animação nomeados
# ─────────────────────────────────────────────────────────────────────────────

class AnimationController:
    """
    Gerencia estados de animação nomeados para um personagem.

    Parâmetros
    ----------
    states  : dict  nome_estado → {anim_key, fps?, loop?}
    scale   : fator de escala para todos os frames
    flipped : espelha todos os frames horizontalmente

    Exemplo
    -------
    ctrl = AnimationController({
        "idle":      {"anim_key": "hero_idle",  "fps": 2,   "loop": True},
        "walk_side": {"anim_key": "hero_walk",  "fps": 8,   "loop": True},
        "attack":    {"anim_key": "hero_attack","fps": 8,   "loop": False},
    }, scale=3)
    ctrl.play("walk_side")
    ctrl.update(dt)
    ctrl.draw(screen, x, y)
    """

    def __init__(self, states: dict, scale: int = 3, flipped: bool = False):
        self._scale   = scale
        self._flipped = flipped
        self._anims: dict[str, AnimatedSprite] = {}
        self._state   = ""
        self._current: AnimatedSprite | None = None

        for name, cfg in states.items():
            key  = cfg["anim_key"]
            fps  = cfg.get("fps", 8.0)
            loop = cfg.get("loop", True)
            self._anims[name] = AnimatedSprite(
                key, scale=scale, fps=fps, flipped=flipped, loop=loop)

        if states:
            self.play(next(iter(states)))

    # ------------------------------------------------------------------
    def play(self, state: str, force_restart: bool = False):
        """Muda para o estado indicado. Se já está neste estado, não reinicia
        a menos que force_restart=True."""
        if state not in self._anims:
            return
        if state == self._state and not force_restart:
            return
        self._state   = state
        self._current = self._anims[state]
        if force_restart:
            self._current.reset()

    def update(self, dt: float):
        if self._current:
            self._current.update(dt)

    def draw(self, screen: pygame.Surface, x: int, y: int):
        if self._current:
            self._current.draw(screen, x, y)

    def reset(self):
        if self._current:
            self._current.reset()

    # ------------------------------------------------------------------
    @property
    def current_state(self) -> str:
        return self._state

    @property
    def is_finished(self) -> bool:
        """True quando animação não-loop chegou ao último frame."""
        if not self._current or self._current.loop:
            return False
        return self._current._index >= len(self._current._frames) - 1

    @property
    def current_frame(self) -> pygame.Surface | None:
        return self._current.current_frame if self._current else None

    @property
    def width(self) -> int:
        return self._current.width if self._current else 0

    @property
    def height(self) -> int:
        return self._current.height if self._current else 0

    # ------------------------------------------------------------------
    @property
    def flipped(self) -> bool:
        return self._flipped

    @flipped.setter
    def flipped(self, value: bool):
        if value == self._flipped:
            return
        self._flipped = value
        for a in self._anims.values():
            a.flipped = value