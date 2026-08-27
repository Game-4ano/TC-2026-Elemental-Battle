"""
HistoricoScene — ranking das melhores pontuacoes salvas.

Herda de GameScene como todas as outras telas, mantendo o mesmo eixo
polimorfico (handle_event / update / draw / render).
"""

import pygame

from meu_jogo.core.game_scene import GameScene
from meu_jogo.core.config import SCREEN_WIDTH, SCREEN_HEIGHT, MAX_HISCORES
from meu_jogo.cenas.menu_scene import desenhar_gradiente


class HistoricoScene(GameScene):
    """Tabela com posicao, nome, pontos e data das melhores partidas."""

    LINHA_H = 26                 # altura de cada linha da tabela
    PAINEL_W = 520
    PAINEL_TOPO = 88

    # Ouro, prata e bronze para os tres primeiros colocados
    CORES_PODIO = [(255, 215, 60), (205, 205, 220), (205, 145, 80)]
    COR_PADRAO  = (200, 200, 220)

    def __init__(self, manager):
        super().__init__(manager)
        # Carrega uma vez: a tela e estatica, nao precisa reler o arquivo por frame.
        self.entradas = self.manager.save.load_scores()

        self._f_titulo  = pygame.font.SysFont(None, 46)
        self._f_normal  = pygame.font.SysFont(None, 24)
        self._f_pequena = pygame.font.SysFont(None, 18)

    # -----------------------------------------------------------------------
    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN and event.key in (
                pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_KP_ENTER):
            self._voltar_ao_menu()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self._voltar_ao_menu()

    def update(self, dt: float):
        pass   # tela estatica

    # -----------------------------------------------------------------------
    def draw(self, screen: pygame.Surface):
        desenhar_gradiente(screen, (10, 5, 30), (30, 15, 60))
        cx = SCREEN_WIDTH // 2

        # Titulo com sombra, no mesmo estilo do menu
        texto  = "Historico de Pontuacao"
        sombra = self._f_titulo.render(texto, True, (80, 50, 0))
        titulo = self._f_titulo.render(texto, True, (255, 220, 60))
        screen.blit(sombra, (cx - titulo.get_width() // 2 + 2, 30))
        screen.blit(titulo, (cx - titulo.get_width() // 2,     28))

        if not self.entradas:
            msg = self._f_normal.render(
                "Nenhuma pontuacao registrada", True, (200, 200, 220))
            screen.blit(msg, (cx - msg.get_width() // 2, SCREEN_HEIGHT // 2 - 20))
            self._draw_rodape(screen)
            return

        self._draw_tabela(screen, cx)
        self._draw_rodape(screen)

    def render(self, screen: pygame.Surface):
        self.draw(screen)

    # -----------------------------------------------------------------------
    def _draw_tabela(self, screen: pygame.Surface, cx: int):
        linhas = self.entradas[:MAX_HISCORES]
        altura = len(linhas) * self.LINHA_H + 42
        painel = pygame.Rect(cx - self.PAINEL_W // 2, self.PAINEL_TOPO,
                             self.PAINEL_W, altura)

        fundo = pygame.Surface(painel.size, pygame.SRCALPHA)
        fundo.fill((12, 8, 30, 215))
        screen.blit(fundo, painel.topleft)
        pygame.draw.rect(screen, (180, 150, 60), painel, 2, border_radius=6)

        # Colunas: posicao e nome alinhados a esquerda, pontos a direita
        col_pos   = painel.x + 20
        col_nome  = painel.x + 62
        col_pts_r = painel.right - 148      # borda direita dos pontos
        col_data  = painel.right - 116

        # Cabecalho
        cab_y = painel.y + 12
        for texto, x in (("#", col_pos), ("Nome", col_nome), ("Data", col_data)):
            screen.blit(self._f_pequena.render(texto, True, (165, 165, 200)), (x, cab_y))
        pts_cab = self._f_pequena.render("Pontos", True, (165, 165, 200))
        screen.blit(pts_cab, (col_pts_r - pts_cab.get_width(), cab_y))
        pygame.draw.line(screen, (90, 80, 140),
                         (painel.x + 12, cab_y + 19),
                         (painel.right - 12, cab_y + 19))

        # Linhas do ranking
        for i, entrada in enumerate(linhas):
            y   = cab_y + 28 + i * self.LINHA_H
            cor = self.CORES_PODIO[i] if i < len(self.CORES_PODIO) else self.COR_PADRAO

            screen.blit(self._f_normal.render(f"{i + 1}", True, cor), (col_pos, y))
            screen.blit(self._f_normal.render(entrada["nome"], True, cor), (col_nome, y))

            pts = self._f_normal.render(str(entrada["pontos"]), True, cor)
            screen.blit(pts, (col_pts_r - pts.get_width(), y))

            if entrada["data"]:
                screen.blit(
                    self._f_pequena.render(entrada["data"], True, (150, 150, 175)),
                    (col_data, y + 4))

    def _draw_rodape(self, screen: pygame.Surface):
        dica = self._f_pequena.render(
            "ESC ou ENTER = voltar ao menu", True, (185, 185, 210))
        screen.blit(dica, (SCREEN_WIDTH // 2 - dica.get_width() // 2,
                           SCREEN_HEIGHT - 30))

    # -----------------------------------------------------------------------
    def _voltar_ao_menu(self):
        # Import local para evitar ciclo com menu_scene.
        from meu_jogo.cenas.menu_scene import MenuScene
        self.manager.audio.play_sfx("menu_select")
        self.manager.scene_manager.change_scene(MenuScene(self.manager))
