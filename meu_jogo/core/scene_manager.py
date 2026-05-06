"""
meu_jogo/core/scene_manager.py

Gerencia a cena ativa com transicao de fade suave entre cenas.
"""

import pygame


class SceneManager:
    # Velocidade do fade em unidades de alpha por segundo (255 / 0.35s ≈ 730)
    _FADE_SPEED = 730

    def __init__(self):
        self.current_scene = None
        self._next_scene   = None
        self._fade_alpha   = 0      # 0 = transparente, 255 = preto
        self._fading_out   = False
        self._fading_in    = False

    # ------------------------------------------------------------------
    def change_scene(self, scene):
        """Troca de cena com fade preto se ja houver uma cena ativa."""
        if self.current_scene is None:
            self.current_scene = scene
        else:
            self._next_scene = scene
            self._fading_out = True
            self._fading_in  = False
            self._fade_alpha = 0

    # ------------------------------------------------------------------
    def handle_event(self, event):
        # Bloqueia entrada durante fade-out para evitar dupla-acao
        if self.current_scene and not self._fading_out:
            self.current_scene.handle_event(event)

    def update(self, dt: float):
        if self.current_scene:
            self.current_scene.update(dt)

        step = int(self._FADE_SPEED * dt) + 1

        if self._fading_out:
            self._fade_alpha = min(255, self._fade_alpha + step)
            if self._fade_alpha >= 255:
                # Troca a cena no pico do escuro
                self.current_scene = self._next_scene
                self._next_scene   = None
                self._fading_out   = False
                self._fading_in    = True

        elif self._fading_in:
            self._fade_alpha = max(0, self._fade_alpha - step)
            if self._fade_alpha <= 0:
                self._fading_in = False

    def render(self, screen: pygame.Surface):
        if self.current_scene:
            self.current_scene.render(screen)

        # Sobreposicao de fade preta
        if (self._fading_out or self._fading_in) and self._fade_alpha > 0:
            veil = pygame.Surface(screen.get_size())
            veil.set_alpha(self._fade_alpha)
            veil.fill((0, 0, 0))
            screen.blit(veil, (0, 0))
