import math
import random
import pygame

from meu_jogo.core.game_scene import GameScene
from meu_jogo.core.config import SCREEN_WIDTH, SCREEN_HEIGHT
from meu_jogo.core.game_state import GameState


def _to_rgb(color):
    """Converte listas/tuplas/pygame.Color para tupla (r,g,b) com ints 0-255."""
    if isinstance(color, pygame.Color):
        return (color.r, color.g, color.b)
    try:
        seq = tuple(int(max(0, min(255, round(c)))) for c in color)
        if len(seq) >= 3:
            return (seq[0], seq[1], seq[2])
    except Exception:
        pass
    return (255, 255, 255)


class VictoryScene(GameScene):
    """Tela de vitoria exibida quando todos os chefes sao derrotados."""

    def __init__(self, manager, summary: dict | None = None):
        super().__init__(manager)
        self.summary   = summary or {}
        self._alpha    = 0
        self._timer    = 0.0
        self._particles: list[dict] = []

        total = self.summary.get("total", 0)
        novo_recorde      = self.manager.save.save_highscore(total)
        self._highscore   = self.manager.save.load_highscore()
        self._novo_record = novo_recorde

        self.manager.audio.play_sfx("victory")
        self._spawn_burst()

    # -----------------------------------------------------------------------
    def _spawn_burst(self):
        cores = [(255, 215, 0), (255, 165, 0), (200, 255, 100), (100, 200, 255)]
        for _ in range(60):
            angle = random.uniform(0, math.tau)
            speed = random.uniform(80, 260)
            self._particles.append({
                "pos":   pygame.Vector2(
                    random.randint(50, SCREEN_WIDTH - 50),
                    random.randint(-40, SCREEN_HEIGHT // 2)),
                "vel":   pygame.Vector2(math.cos(angle) * speed,
                                        math.sin(angle) * speed + 30),
                "life":  random.uniform(1.5, 3.5),
                "color": random.choice(cores),
                "r":     random.randint(3, 8),
            })

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            self._ir_para_menu()

    def update(self, dt: float):
        self._alpha = min(255, self._alpha + int(dt * 200))
        self._timer += dt

        for p in self._particles:
            p["pos"] += p["vel"] * dt
            p["vel"].y += 120 * dt
            p["life"]  -= dt
        self._particles = [p for p in self._particles if p["life"] > 0]

        if self._timer > 1.0 and len(self._particles) < 40:
            self._spawn_burst()

    def draw(self, screen: pygame.Surface):
        # Fundo degradê dourado
        for y in range(SCREEN_HEIGHT):
            t = y / SCREEN_HEIGHT
            r = int(20 + 30 * t)
            g = int(10 + 20 * t)
            pygame.draw.line(screen, (r, g, 0), (0, y), (SCREEN_WIDTH, y))

        # Confetes
        for p in self._particles:
            alpha = int(255 * max(p["life"], 0) / 3.5)
            s = pygame.Surface((p["r"] * 2, p["r"] * 2), pygame.SRCALPHA)
            _rgb = _to_rgb(p["color"])
            pygame.draw.circle(s, (_rgb[0], _rgb[1], _rgb[2], alpha), (p["r"], p["r"]), p["r"])
            screen.blit(s, (int(p["pos"].x) - p["r"], int(p["pos"].y) - p["r"]))

        # Texto com fade-in
        surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        surf.set_alpha(self._alpha)

        f_titulo = pygame.font.SysFont(None, 96)
        f_sub    = pygame.font.SysFont(None, 36)
        f_sm     = pygame.font.SysFont(None, 26)

        titulo = f_titulo.render("VITORIA!", True, (255, 215, 0))
        sub    = f_sub.render("Todos os chefes foram derrotados!", True, (255, 240, 180))

        cx = SCREEN_WIDTH  // 2
        cy = SCREEN_HEIGHT // 2

        surf.blit(titulo, (cx - titulo.get_width() // 2, cy - 140))
        surf.blit(sub,    (cx - sub.get_width()    // 2, cy - 50))

        total = self.summary.get("total", 0)
        score_txt = f_sm.render(f"Pontuacao final: {total}", True, (255, 215, 0))
        surf.blit(score_txt, (cx - score_txt.get_width() // 2, cy))

        if self._novo_record:
            rec = f_sm.render("NOVO RECORDE!", True, (255, 100, 100))
            surf.blit(rec, (cx - rec.get_width() // 2, cy + 30))
        else:
            rec = f_sm.render(f"Recorde: {self._highscore}", True, (200, 200, 200))
            surf.blit(rec, (cx - rec.get_width() // 2, cy + 30))

        hint = f_sm.render("ENTER = Continuar", True, (160, 200, 160))
        surf.blit(hint, (cx - hint.get_width() // 2, cy + 80))

        screen.blit(surf, (0, 0))

    def render(self, screen: pygame.Surface):
        self.draw(screen)

    # -----------------------------------------------------------------------
    def _ir_para_menu(self):
        from meu_jogo.cenas.campo_de_treino import CampoDeTreinoScene
        player = self.manager.game.player
        player.hp = player.max_hp
        self.manager.map_manager.load_map("MUNDO_ABERTO")
        self.manager.scene_manager.change_scene(
            CampoDeTreinoScene(self.manager))
