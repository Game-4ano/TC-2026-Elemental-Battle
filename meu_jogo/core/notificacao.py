"""
meu_jogo/core/notificacao.py

Sistema de notificações flutuantes na parte superior da tela.
Qualquer parte do jogo pode exibir uma mensagem chamando:

    manager.notificacoes.adicionar("Texto aqui")
    manager.notificacoes.adicionar("Level up!", cor=(255, 220, 50), duracao=3.0)

O NotificationSystem é atualizado e desenhado pelo GameManager
automaticamente em todo frame, por cima de qualquer cena ativa.
"""

import pygame


class _Notificacao:
    """Uma única mensagem flutuante."""

    def __init__(self, texto: str, cor: tuple, duracao: float, fonte):
        self.texto    = texto
        self.cor      = cor
        self.duracao  = duracao   # tempo total de vida (segundos)
        self._timer   = 0.0       # tempo decorrido

        # Fade: aparece em 0.3s, some nos últimos 0.5s
        self.FADE_IN  = 0.3
        self.FADE_OUT = 0.5

        self._surface = fonte.render(texto, True, cor)

    @property
    def vivo(self) -> bool:
        return self._timer < self.duracao

    @property
    def alpha(self) -> int:
        t = self._timer
        d = self.duracao
        if t < self.FADE_IN:
            return int(255 * (t / self.FADE_IN))
        if t > d - self.FADE_OUT:
            return int(255 * ((d - t) / self.FADE_OUT))
        return 255

    def update(self, dt: float):
        self._timer += dt

    def draw(self, screen: pygame.Surface, y: int, screen_w: int):
        surf = self._surface.copy()
        surf.set_alpha(self.alpha)
        x = screen_w // 2 - surf.get_width() // 2
        screen.blit(surf, (x, y))

    @property
    def height(self) -> int:
        return self._surface.get_height()


class NotificationSystem:
    """
    Gerencia uma pilha de notificações e as desenha empilhadas
    no topo da tela, uma abaixo da outra.
    """

    MARGEM_TOPO = 10   # px do topo da tela até a primeira notificação
    ESPACO      = 4    # px entre notificações

    def __init__(self, screen_w: int):
        self._screen_w      = screen_w
        self._notificacoes: list[_Notificacao] = []
        self._fonte         = pygame.font.SysFont(None, 26)
        self._fonte_destaque = pygame.font.SysFont(None, 30)

    # ------------------------------------------------------------------
    def adicionar(
        self,
        texto: str,
        cor: tuple = (255, 255, 255),
        duracao: float = 2.5,
        destaque: bool = False,
    ):
        """
        Adiciona uma nova notificação.

        Parâmetros
        ----------
        texto    : mensagem a exibir
        cor      : cor RGB do texto
        duracao  : quantos segundos a mensagem fica visível
        destaque : se True usa fonte maior (para level up, vitória, etc.)
        """
        fonte = self._fonte_destaque if destaque else self._fonte
        self._notificacoes.append(
            _Notificacao(texto, cor, duracao, fonte)
        )

    # ------------------------------------------------------------------
    def update(self, dt: float):
        for n in self._notificacoes:
            n.update(dt)
        self._notificacoes = [n for n in self._notificacoes if n.vivo]

    def draw(self, screen: pygame.Surface):
        y = self.MARGEM_TOPO
        for n in self._notificacoes:
            # Fundo semitransparente atrás do texto
            w = n._surface.get_width() + 20
            h = n.height + 6
            bg = pygame.Surface((w, h), pygame.SRCALPHA)
            bg.fill((0, 0, 0, int(140 * (n.alpha / 255))))
            screen.blit(bg, (self._screen_w // 2 - w // 2, y - 3))

            n.draw(screen, y, self._screen_w)
            y += n.height + self.ESPACO