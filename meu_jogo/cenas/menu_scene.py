"""
meu_jogo/cenas/menu_scene.py

Tela de título e seleção de elemento do jogador.

Fluxo:
    1. TITULO   — nome do jogo + "Aperte qualquer tecla para começar"
    2. SELECAO  — diagrama de vantagens elementais + escolha do elemento
    3. (inicia o jogo → CampoDeTreinoScene)
"""

import math
import random
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

        # 3-layer parallax stars
        _sc = [(200,180,255),(180,210,255),(255,230,200),(160,230,255)]
        def _mk(count, sp_lo, sp_hi, r_lo, r_hi, dr):
            return [{"pos": pygame.Vector2(random.randint(0, SCREEN_WIDTH),
                                           random.randint(0, SCREEN_HEIGHT)),
                     "phase": random.uniform(0, math.tau),
                     "speed": random.uniform(sp_lo, sp_hi),
                     "drift": random.uniform(-dr, dr),
                     "r":     random.randint(r_lo, r_hi),
                     "color": random.choice(_sc)}
                    for _ in range(count)]
        self._stars_layers = [
            _mk(20, 0.15, 0.40, 1, 1,  3),
            _mk(22, 0.60, 1.50, 1, 2,  6),
            _mk(13, 1.80, 3.00, 2, 3, 10),
        ]

        # Boss silhouettes drifting across title screen
        _sc2 = [(30,120,220),(220,70,20),(200,170,0),(40,160,50),(100,30,170)]
        self._silhouettes = [
            {"x": SCREEN_WIDTH * (0.12 + 0.18*i),
             "y": random.randint(60, 340),
             "dx": random.uniform(-14, -7),
             "color": _sc2[i], "stype": i}
            for i in range(5)
        ]

        self._title_color_t = 0.0
        self._modal: str | None = None

        self.manager.audio.play_music("menu_theme", volume=0.45)

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
        if self._modal is not None:
            if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                self._modal = None
            return

        if self.fase == self.FASE_TITULO:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                cy = SCREEN_HEIGHT // 2
                btn1 = pygame.Rect(SCREEN_WIDTH//2 - 168, cy + 94, 156, 26)
                btn2 = pygame.Rect(SCREEN_WIDTH//2 + 12,  cy + 94, 156, 26)
                if btn1.collidepoint(mx, my):
                    self._modal = "como_jogar"
                    return
                if btn2.collidepoint(mx, my):
                    self._modal = "creditos"
                    return
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

        self._title_color_t += dt * 0.7
        speed_mults = [0.4, 1.0, 2.2]
        for li, layer in enumerate(self._stars_layers):
            sm = speed_mults[li]
            for s in layer:
                s["phase"] += dt * s["speed"]
                s["pos"].y -= 6 * dt * sm
                s["pos"].x += s["drift"] * dt * 0.15
                if s["pos"].y < -4:
                    s["pos"].y = SCREEN_HEIGHT + 4
                    s["pos"].x = random.randint(0, SCREEN_WIDTH)
        for silh in self._silhouettes:
            silh["x"] += silh["dx"] * dt
            if silh["x"] < -120:
                silh["x"] = SCREEN_WIDTH + 80
                silh["y"] = random.randint(60, 340)

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
        self.manager.audio.play_sfx("menu_select")
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
        if self._modal:
            self._draw_modal(screen)

    def render(self, screen):
        self.draw(screen)

    # -----------------------------------------------------------------------
    def _draw_stars(self, screen):
        base_alphas = [50, 80, 115]
        for li, layer in enumerate(self._stars_layers):
            ba = base_alphas[li]
            for s in layer:
                alpha = int(ba + 50 * math.sin(s["phase"]))
                r     = s["r"]
                surf  = pygame.Surface((r * 2 + 2, r * 2 + 2), pygame.SRCALPHA)
                pygame.draw.circle(surf, (*s["color"], alpha), (r + 1, r + 1), r)
                screen.blit(surf, (int(s["pos"].x) - r - 1, int(s["pos"].y) - r - 1))

    def _draw_silhouettes(self, screen):
        for silh in self._silhouettes:
            sx, sy  = int(silh["x"]), int(silh["y"])
            col     = (*silh["color"], 38)
            stype   = silh["stype"]
            W = H = 90
            s = pygame.Surface((W, H), pygame.SRCALPHA)
            if stype == 0:   # Hydra — blob + heads
                pygame.draw.ellipse(s, col, (12, 40, 66, 45))
                for hx in (20, 40, 62):
                    pygame.draw.ellipse(s, col, (hx - 7, 8, 14, 30))
            elif stype == 1: # Magma Titan — wide mass + spikes
                pygame.draw.rect(s, col, (10, 28, 70, 52), border_radius=4)
                for bx in (18, 38, 58, 76):
                    pygame.draw.polygon(s, col, [(bx-7, 28),(bx, 6),(bx+7, 28)])
            elif stype == 2: # Storm Eagle — spread wings
                pygame.draw.ellipse(s, col, (30, 32, 30, 32))
                pygame.draw.polygon(s, col, [(0,52),(30,36),(45,56),(15,66)])
                pygame.draw.polygon(s, col, [(90,52),(60,36),(45,56),(75,66)])
            elif stype == 3: # Thunder Beast — angular body
                pygame.draw.polygon(s, col,
                    [(5,82),(20,32),(40,10),(60,32),(75,82),(50,62),(40,72),(30,62)])
            else:            # Shadow Lord — hooded figure
                pygame.draw.ellipse(s, col, (28, 4, 34, 28))
                pygame.draw.polygon(s, col,
                    [(4,86),(18,42),(34,30),(56,30),(72,42),(86,86),(62,72),(45,82),(28,72)])
            screen.blit(s, (sx - W // 2, sy - H // 2))

    def _bg_gradient(self, screen, top, bot):
        for i in range(SCREEN_HEIGHT):
            t = i / SCREEN_HEIGHT
            c = tuple(int(top[j] + (bot[j] - top[j]) * t) for j in range(3))
            pygame.draw.line(screen, c, (0, i), (SCREEN_WIDTH, i))

    def _draw_titulo(self, screen):
        self._bg_gradient(screen, (10, 5, 30), (30, 15, 60))
        self._draw_silhouettes(screen)
        self._draw_stars(screen)

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

        # Título com cores de elemento ciclando por letra
        title  = "ELEMENTAL BATTLE"
        total_w = sum(self._f_titulo.size(ch)[0] for ch in title)
        x_cur   = SCREEN_WIDTH // 2 - total_w // 2
        ty      = cy - 90
        for ci, ch in enumerate(title):
            cidx     = int(self._title_color_t * 2 + ci * 0.55) % len(ELEMENTOS)
            ch_color = ELEMENTOS[cidx]["cor_clara"]
            sh_s = self._f_titulo.render(ch, True, (40, 20, 0))
            ch_s = self._f_titulo.render(ch, True, ch_color)
            screen.blit(sh_s, (x_cur + 3, ty + 3))
            screen.blit(ch_s, (x_cur,     ty))
            x_cur += ch_s.get_width()

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

        # Recorde salvo
        hs = self.manager.save.load_highscore()
        if hs > 0:
            hs_txt = self._f_pequena.render(f"Recorde: {hs}", True, (200, 180, 80))
            screen.blit(hs_txt, (SCREEN_WIDTH // 2 - hs_txt.get_width() // 2, cy + 74))

        # Botões "Como jogar?" e "Créditos"
        btn_w, btn_h = 156, 26
        btn_y = cy + 94
        for btn_x, label in [
            (SCREEN_WIDTH//2 - btn_w - 12, "Como jogar?"),
            (SCREEN_WIDTH//2 + 12,          "Creditos"),
        ]:
            bsurf = pygame.Surface((btn_w, btn_h), pygame.SRCALPHA)
            bsurf.fill((15, 10, 40, 180))
            screen.blit(bsurf, (btn_x, btn_y))
            pygame.draw.rect(screen, (120, 100, 180),
                             (btn_x, btn_y, btn_w, btn_h), 1, border_radius=4)
            bl = self._f_normal.render(label, True, (200, 200, 255))
            screen.blit(bl, (btn_x + btn_w//2 - bl.get_width()//2,
                             btn_y + btn_h//2 - bl.get_height()//2))

        # Créditos
        cred = self._f_pequena.render(
            "Artur Flacon  *  Eduardo Ceciliato  *  Vinicius de Oliveira",
            True, (110, 110, 145))
        screen.blit(cred, (SCREEN_WIDTH // 2 - cred.get_width() // 2, SCREEN_HEIGHT - 28))

    # -----------------------------------------------------------------------
    def _draw_selecao(self, screen):
        self._bg_gradient(screen, (8, 8, 25), (20, 15, 45))
        self._draw_stars(screen)

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

        # Descrição do elemento em hover
        if self._hover_idx >= 0:
            elem      = ELEMENTOS[self._hover_idx]
            beats_key = next((v for a, v in VANTAGENS if a == elem["key"]), None)
            beats_nome = next(
                (e["nome"] for e in ELEMENTOS if e["key"] == beats_key), "—"
            ) if beats_key else "—"
            fraco_nome = next(e["nome"] for e in ELEMENTOS if e["key"] == elem["fraqueza"])
            desc  = f'{elem["nome"]}  |  Forte: {beats_nome}   Fraco: {fraco_nome}'
            bg_d  = pygame.Surface((SCREEN_WIDTH - 16, 22), pygame.SRCALPHA)
            bg_d.fill((0, 0, 0, 160))
            screen.blit(bg_d, (8, 422))
            d_s = self._f_normal.render(desc, True, elem["cor_clara"])
            screen.blit(d_s, (SCREEN_WIDTH//2 - d_s.get_width()//2, 425))

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

    # -----------------------------------------------------------------------
    def _draw_modal(self, screen):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 185))
        screen.blit(overlay, (0, 0))

        w, h   = 460, 270
        mx, my = SCREEN_WIDTH//2 - w//2, SCREEN_HEIGHT//2 - h//2
        panel  = pygame.Surface((w, h), pygame.SRCALPHA)
        panel.fill((12, 8, 30, 245))
        screen.blit(panel, (mx, my))
        pygame.draw.rect(screen, (180, 150, 60), (mx, my, w, h), 2, border_radius=6)
        pygame.draw.rect(screen, (80, 60, 20),
                         (mx + 4, my + 4, w - 8, h - 8), 1, border_radius=4)

        if self._modal == "como_jogar":
            titulo = "Como Jogar"
            linhas = [
                "Setas <- -> ^  v  —  Mover no mapa",
                "Caminhar sobre portal  —  Iniciar batalha",
                "",
                "Na batalha:",
                "Setas / WASD  —  Navegar acoes",
                "ENTER ou ESPACO  —  Confirmar acao",
                "",
                "Elementos tem vantagens entre si.",
                "Derrote todos os chefes elementais!",
            ]
        else:
            titulo = "Creditos"
            linhas = [
                "Artur Flacon",
                "Eduardo Ceciliato",
                "Vinicius de Oliveira",
                "",
                "TC-2026  —  Topicos em Computacao",
                "Desenvolvido com Python + Pygame",
            ]

        t_s = self._f_sub.render(titulo, True, (255, 220, 60))
        screen.blit(t_s, (mx + w//2 - t_s.get_width()//2, my + 16))
        pygame.draw.line(screen, (160, 130, 50), (mx + 20, my + 44), (mx + w - 20, my + 44), 1)

        for i, linha in enumerate(linhas):
            if not linha:
                continue
            cor = (255, 220, 120) if linha.endswith(":") else (200, 200, 230)
            l_s = self._f_normal.render(linha, True, cor)
            screen.blit(l_s, (mx + 24, my + 54 + i * 20))

        esc = self._f_pequena.render("Pressione qualquer tecla para fechar", True, (140, 140, 180))
        screen.blit(esc, (mx + w//2 - esc.get_width()//2, my + h - 22))