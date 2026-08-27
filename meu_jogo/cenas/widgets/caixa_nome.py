"""
CaixaDeNome — componente reutilizavel de entrada de texto.

NAO herda de GameScene: e um widget usado *dentro* de uma cena. VictoryScene e
GameOverScene compartilham esta mesma classe em vez de duplicar a logica de
digitacao.
"""

import pygame


class CaixaDeNome:
    """Caixa de texto com cursor piscando, usada para capturar o nome do jogador."""

    LARGURA = 260
    ALTURA  = 44
    PISCA_S = 0.5   # meio segundo por ciclo do cursor

    def __init__(self, max_len: int, on_confirm):
        """on_confirm(nome: str) e chamado quando o jogador aperta ENTER."""
        self.max_len    = max_len
        self.on_confirm = on_confirm
        self._texto     = ""
        self._cursor_on = True
        self._timer     = 0.0
        self._font      = pygame.font.SysFont(None, 34)
        self._font_dica = pygame.font.SysFont(None, 20)

    @property
    def texto(self) -> str:
        return self._texto

    # -----------------------------------------------------------------------
    def handle_event(self, event: pygame.event.Event):
        if event.type != pygame.KEYDOWN:
            return

        if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            # Nome vazio e permitido de proposito (nao prende o jogador na
            # caixa): o SaveSystem grava "---" quando recebe string vazia.
            self.on_confirm(self._texto.strip())
        elif event.key == pygame.K_BACKSPACE:
            self._texto = self._texto[:-1]
        elif len(self._texto) < self.max_len:
            ch = event.unicode
            # Só caracteres imprimiveis (descarta ESC, tab, teclas de controle).
            if ch and ch.isprintable():
                self._texto += ch

    def update(self, dt: float):
        self._timer += dt
        if self._timer >= self.PISCA_S:
            self._timer     = 0.0
            self._cursor_on = not self._cursor_on

    def draw(self, screen: pygame.Surface, centro: pygame.Vector2):
        """Desenha a caixa centrada em `centro` (posicao em pixels)."""
        rect        = pygame.Rect(0, 0, self.LARGURA, self.ALTURA)
        rect.center = (int(centro.x), int(centro.y))

        # Fundo + borda dourada, no estilo dos paineis do jogo
        fundo = pygame.Surface(rect.size, pygame.SRCALPHA)
        fundo.fill((10, 8, 24, 225))
        screen.blit(fundo, rect.topleft)
        pygame.draw.rect(screen, (200, 180, 90), rect, 2, border_radius=6)

        # Texto digitado + cursor piscando
        cursor = "|" if self._cursor_on else " "
        txt    = self._font.render(self._texto + cursor, True, (255, 255, 255))
        screen.blit(txt, (rect.x + 12, rect.centery - txt.get_height() // 2))

        # Dica acima da caixa
        dica = self._font_dica.render(
            "Digite seu nome e pressione ENTER", True, (205, 205, 225))
        screen.blit(dica, (rect.centerx - dica.get_width() // 2, rect.top - 22))
