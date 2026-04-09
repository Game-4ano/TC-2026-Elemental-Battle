"""
meu_jogo/cenas/menu_scene.py

Tela de título e seleção de elemento do jogador.

Fluxo:
    1. TITULO   — nome do jogo + "Aperte qualquer tecla para começar"
    2. SELECAO  — diagrama de vantagens elementais + escolha do elemento
    3. (inicia o jogo → CampoDeTreinoScene)
"""

import math
import pygame

from meu_jogo.core.game_scene import GameScene
from meu_jogo.core.config import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, BLACK


# ─────────────────────────────────────────────────────────────────────────────
#  Dados de cada elemento
# ─────────────────────────────────────────────────────────────────────────────

ELEMENTOS = [
    {
        "key":      "Fire",
        "nome":     "Fogo",
        "fraqueza": "Water",
        "cor":      (220,  70,  20),
        "cor_clara":(255, 140,  60),
        "tecla":    pygame.K_1,
        "label":    "[1]",
    },
    {
        "key":      "Water",
        "nome":     "Agua",
        "fraqueza": "Electric",
        "cor":      ( 30, 120, 220),
        "cor_clara":( 90, 180, 255),
        "tecla":    pygame.K_2,
        "label":    "[2]",
    },
    {
        "key":      "Grass",
        "nome":     "Planta",
        "fraqueza": "Fire",
        "cor":      ( 40, 160,  50),
        "cor_clara":( 90, 220,  90),
        "tecla":    pygame.K_3,
        "label":    "[3]",
    },
    {
        "key":      "Electric",
        "nome":     "Eletrico",
        "fraqueza": "Grass",
        "cor":      (200, 170,   0),
        "cor_clara":(255, 230,  60),
        "tecla":    pygame.K_4,
        "label":    "[4]",
    },
    {
        "key":      "Dark",
        "nome":     "Sombra",
        "fraqueza": "Electric",
        "cor":      (100,  30, 170),
        "cor_clara":(170,  80, 240),
        "tecla":    pygame.K_5,
        "label":    "[5]",
    },
]

# Quem vence quem: atacante derrota vitima
VANTAGENS = [
    ("Fire",     "Grass"),
    ("Water",    "Fire"),
    ("Grass",    "Water"),
    ("Electric", "Water"),
    ("Dark",     "Fire"),
]


# ─────────────────────────────────────────────────────────────────────────────
#  Helpers de desenho
# ─────────────────────────────────────────────────────────────────────────────

def _draw_symbol(surface, elem, cx, cy, raio, hover=False):
    cor       = elem["cor"]
    cor_clara = elem["cor_clara"]

    if hover:
        glow = pygame.Surface((raio * 3, raio * 3), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*cor_clara, 60),
                           (raio * 3 // 2, raio * 3 // 2), raio + 10)
        surface.blit(glow, (cx - raio * 3 // 2, cy - raio * 3 // 2))
        pygame.draw.circle(surface, cor_clara, (cx, cy), raio + 5, 3)

    pygame.draw.circle(surface, cor, (cx, cy), raio)
    # Brilho interno
    pygame.draw.circle(surface, cor_clara,
                       (cx - raio // 4, cy - raio // 4), raio // 3)
    # Borda branca
    pygame.draw.circle(surface, (255, 255, 255), (cx, cy), raio, 2)

    # Nome centralizado no círculo
    fonte = pygame.font.SysFont(None, 19)
    txt   = fonte.render(elem["nome"], True, (255, 255, 255))
    surface.blit(txt, (cx - txt.get_width() // 2, cy - txt.get_height() // 2))


def _draw_arrow(surface, x1, y1, x2, y2, cor, raio_skip=40):
    dx   = x2 - x1
    dy   = y2 - y1
    dist = math.hypot(dx, dy)
    if dist == 0:
        return
    ux, uy = dx / dist, dy / dist
    sx = x1 + ux * raio_skip
    sy = y1 + uy * raio_skip
    ex = x2 - ux * raio_skip
    ey = y2 - uy * raio_skip
    pygame.draw.line(surface, cor, (int(sx), int(sy)), (int(ex), int(ey)), 2)
    head  = 10
    angle = math.atan2(ey - sy, ex - sx)
    for side in (+0.45, -0.45):
        ax = ex - head * math.cos(angle - side)
        ay = ey - head * math.sin(angle - side)
        pygame.draw.line(surface, cor,
                         (int(ex), int(ey)), (int(ax), int(ay)), 2)


def _draw_legend_arrow(surface, x, y, cor):
    pygame.draw.line(surface, cor, (x, y), (x + 22, y), 2)
    pygame.draw.line(surface, cor, (x + 22, y), (x + 14, y - 4), 2)
    pygame.draw.line(surface, cor, (x + 22, y), (x + 14, y + 4), 2)


# ─────────────────────────────────────────────────────────────────────────────
#  Cena
# ─────────────────────────────────────────────────────────────────────────────

class MenuScene(GameScene):

    FASE_TITULO  = "titulo"
    FASE_SELECAO = "selecao"

    def __init__(self, manager):
        super().__init__(manager)
        self.fase = self.FASE_TITULO

        self._f_titulo   = pygame.font.SysFont(None, 52)
        self._f_sub      = pygame.font.SysFont(None, 28)
        self._f_normal   = pygame.font.SysFont(None, 22)
        self._f_pequena  = pygame.font.SysFont(None, 18)

        self._blink_timer = 0.0
        self._blink_vis   = True
        self._arrow_timer = 0.0
        self._hover_idx   = -1

        # Posições dos 5 elementos em pentágono centrado na tela
        self._elem_pos = self._calcular_posicoes()

    # -----------------------------------------------------------------------
    def _calcular_posicoes(self):
        cx0 = SCREEN_WIDTH  // 2
        cy0 = SCREEN_HEIGHT // 2 + 20
        r   = 130
        n   = len(ELEMENTOS)
        pos = []
        for i in range(n):
            ang = -math.pi / 2 + (2 * math.pi * i / n)
            pos.append((int(cx0 + r * math.cos(ang)),
                        int(cy0 + r * math.sin(ang))))
        return pos

    # -----------------------------------------------------------------------
    def handle_event(self, event):
        if self.fase == self.FASE_TITULO:
            if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                self.fase = self.FASE_SELECAO

        elif self.fase == self.FASE_SELECAO:
            if event.type == pygame.KEYDOWN:
                for elem in ELEMENTOS:
                    if event.key == elem["tecla"]:
                        self._iniciar_jogo(elem)
                        return
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                idx = self._elem_sob_mouse(*pygame.mouse.get_pos())
                if idx >= 0:
                    self._iniciar_jogo(ELEMENTOS[idx])

    def update(self, dt):
        self._blink_timer += dt
        if self._blink_timer >= 0.55:
            self._blink_timer = 0.0
            self._blink_vis   = not self._blink_vis
        self._arrow_timer += dt
        if self.fase == self.FASE_SELECAO:
            self._hover_idx = self._elem_sob_mouse(*pygame.mouse.get_pos())

    # -----------------------------------------------------------------------
    def _elem_sob_mouse(self, mx, my):
        for i, (cx, cy) in enumerate(self._elem_pos):
            if math.hypot(mx - cx, my - cy) <= 42:
                return i
        return -1

    def _iniciar_jogo(self, elem):
        player          = self.manager.game.player
        player.element  = elem["key"]
        player.weakness = elem["fraqueza"]
        self.manager.notificacoes.adicionar(
            f"Elemento escolhido: {elem['nome']}!",
            cor=elem["cor_clara"],
            duracao=2.5,
        )
        from meu_jogo.cenas.campo_de_treino import CampoDeTreinoScene
        self.manager.scene_manager.change_scene(
            CampoDeTreinoScene(self.manager)
        )

    # -----------------------------------------------------------------------
    def draw(self, screen):
        if self.fase == self.FASE_TITULO:
            self._draw_titulo(screen)
        else:
            self._draw_selecao(screen)

    def render(self, screen):
        self.draw(screen)

    # -----------------------------------------------------------------------
    def _bg_gradient(self, screen, top, bot):
        for i in range(SCREEN_HEIGHT):
            t = i / SCREEN_HEIGHT
            c = tuple(int(top[j] + (bot[j] - top[j]) * t) for j in range(3))
            pygame.draw.line(screen, c, (0, i), (SCREEN_WIDTH, i))

    def _draw_titulo(self, screen):
        self._bg_gradient(screen, (10, 5, 30), (30, 15, 60))

        # Círculos decorativos de fundo
        decos = [
            (70,  70,  0), (430, 70,  1), (70,  430, 2),
            (430, 430, 3), (250, 430, 4),
        ]
        for (dx, dy, ei) in decos:
            e  = ELEMENTOS[ei]
            s  = pygame.Surface((130, 130), pygame.SRCALPHA)
            pygame.draw.circle(s, (*e["cor"], 35),     (65, 65), 58)
            pygame.draw.circle(s, (*e["cor_clara"], 18),(65, 65), 58, 3)
            screen.blit(s, (dx - 65, dy - 65))

        cy = SCREEN_HEIGHT // 2

        # Sombra + título
        t_surf  = self._f_titulo.render("ELEMENTAL BATTLE", True, (255, 220, 60))
        sh_surf = self._f_titulo.render("ELEMENTAL BATTLE", True, (80,  50,  0))
        tx = SCREEN_WIDTH // 2 - t_surf.get_width() // 2
        screen.blit(sh_surf, (tx + 3, cy - 90 + 3))
        screen.blit(t_surf,  (tx,     cy - 90))

        # Linha decorativa
        lw = 240
        lx = SCREEN_WIDTH // 2 - lw // 2
        pygame.draw.line(screen, (200, 160, 40), (lx, cy - 54), (lx + lw, cy - 54), 2)

        # Subtítulo
        sub = self._f_sub.render("Batalhas elementais por turno", True, (180, 180, 210))
        screen.blit(sub, (SCREEN_WIDTH // 2 - sub.get_width() // 2, cy - 42))

        # "Aperte qualquer tecla" piscando
        if self._blink_vis:
            msg = self._f_sub.render("Aperte qualquer tecla para comecar", True, (220, 220, 255))
            screen.blit(msg, (SCREEN_WIDTH // 2 - msg.get_width() // 2, cy + 40))

        # Créditos
        cred = self._f_pequena.render(
            "Arthur Flacon  *  Eduardo Ceciliato  *  Vinicius de Oliveira",
            True, (110, 110, 145))
        screen.blit(cred, (SCREEN_WIDTH // 2 - cred.get_width() // 2, SCREEN_HEIGHT - 28))

    # -----------------------------------------------------------------------
    def _draw_selecao(self, screen):
        self._bg_gradient(screen, (8, 8, 25), (20, 15, 45))

        # Título compacto no topo
        t_surf  = self._f_titulo.render("ELEMENTAL BATTLE", True, (255, 220, 60))
        sh_surf = self._f_titulo.render("ELEMENTAL BATTLE", True, (80,  50,  0))
        tx = SCREEN_WIDTH // 2 - t_surf.get_width() // 2
        screen.blit(sh_surf, (tx + 2, 12))
        screen.blit(t_surf,  (tx,     10))

        inst = self._f_sub.render("Escolha seu elemento", True, (200, 200, 240))
        screen.blit(inst, (SCREEN_WIDTH // 2 - inst.get_width() // 2, 58))

        # --- Diagrama de vantagens ---
        pos_map = {e["key"]: self._elem_pos[i] for i, e in enumerate(ELEMENTOS)}

        # Setas pulsantes
        pulse = int(180 + 70 * math.sin(self._arrow_timer * 2.5))
        for (atacante, vitima) in VANTAGENS:
            p1      = pos_map[atacante]
            p2      = pos_map[vitima]
            base    = next(e["cor_clara"] for e in ELEMENTOS if e["key"] == atacante)
            cor_p   = tuple(int(c * pulse / 255) for c in base)
            _draw_arrow(screen, p1[0], p1[1], p2[0], p2[1], cor_p)

        # Rótulo "vence" no meio de cada seta
        f_tiny = pygame.font.SysFont(None, 16)
        for (atacante, vitima) in VANTAGENS:
            p1 = pos_map[atacante]
            p2 = pos_map[vitima]
            mx = (p1[0] + p2[0]) // 2
            my = (p1[1] + p2[1]) // 2
            lbl = f_tiny.render("vence", True, (200, 200, 200))
            # fundo mini
            bg = pygame.Surface((lbl.get_width() + 4, lbl.get_height() + 2), pygame.SRCALPHA)
            bg.fill((0, 0, 0, 140))
            screen.blit(bg, (mx - lbl.get_width() // 2 - 2, my - lbl.get_height() // 2 - 1))
            screen.blit(lbl, (mx - lbl.get_width() // 2, my - lbl.get_height() // 2))

        # Círculos dos elementos (hover dinâmico)
        for i, elem in enumerate(ELEMENTOS):
            cx, cy = self._elem_pos[i]
            _draw_symbol(screen, elem, cx, cy, raio=38,
                         hover=(i == self._hover_idx))

        # Tecla de seleção abaixo de cada círculo
        for i, elem in enumerate(ELEMENTOS):
            cx, cy = self._elem_pos[i]
            lbl = self._f_normal.render(elem["label"], True, elem["cor_clara"])
            screen.blit(lbl, (cx - lbl.get_width() // 2, cy + 46))

        # --- Legenda rodapé ---
        leg_y = SCREEN_HEIGHT - 48
        box   = pygame.Rect(8, leg_y - 4, SCREEN_WIDTH - 16, 42)
        bg    = pygame.Surface((box.w, box.h), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 150))
        screen.blit(bg, (box.x, box.y))
        pygame.draw.rect(screen, (70, 70, 110), box, 1, border_radius=4)

        _draw_legend_arrow(screen, 18, leg_y + 9, (200, 200, 200))
        leg1 = self._f_pequena.render(
            "A seta mostra quem vence quem  |  Clique ou [1-5] para escolher",
            True, (180, 180, 215))
        screen.blit(leg1, (50, leg_y + 3))

        partes = []
        for e in ELEMENTOS:
            fraco = next(x["nome"] for x in ELEMENTOS if x["key"] == e["fraqueza"])
            partes.append(f"{e['nome']} perde para {fraco}")
        leg2 = self._f_pequena.render("   |   ".join(partes), True, (120, 120, 155))
        screen.blit(leg2, (SCREEN_WIDTH // 2 - leg2.get_width() // 2, leg_y + 22))