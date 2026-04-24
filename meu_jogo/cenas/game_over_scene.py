import pygame

from meu_jogo.core.game_scene import GameScene
from meu_jogo.core.config import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE
from meu_jogo.core.game_state import GameState


class GameOverScene(GameScene):
    """Tela exibida quando o jogador e derrotado."""

    def __init__(self, manager, total_score: int = 0):
        super().__init__(manager)
        self.total_score = total_score
        self._alpha      = 0
        self._fade_done  = False

        novo_recorde = self.manager.save.save_highscore(total_score)
        self._highscore   = self.manager.save.load_highscore()
        self._novo_record = novo_recorde

        self.manager.audio.play_sfx("defeat")

    # -----------------------------------------------------------------------
    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            self._ir_para_menu()

    def update(self, dt: float):
        if not self._fade_done:
            self._alpha = min(255, self._alpha + int(dt * 280))
            if self._alpha >= 255:
                self._fade_done = True

    def draw(self, screen: pygame.Surface):
        screen.fill((8, 0, 0))

        # Vinheta vermelha nas bordas
        vignette = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        for r in range(0, min(SCREEN_WIDTH, SCREEN_HEIGHT) // 2, 4):
            alpha = int(120 * (1 - r / (min(SCREEN_WIDTH, SCREEN_HEIGHT) // 2)))
            pygame.draw.rect(vignette, (160, 0, 0, alpha),
                             (r, r, SCREEN_WIDTH - r * 2, SCREEN_HEIGHT - r * 2), 4)
        screen.blit(vignette, (0, 0))

        surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        surf.set_alpha(self._alpha)

        f_titulo = pygame.font.SysFont(None, 96)
        f_sub    = pygame.font.SysFont(None, 34)
        f_hint   = pygame.font.SysFont(None, 26)

        titulo = f_titulo.render("GAME OVER", True, (200, 30, 30))
        sub    = f_sub.render("Voce foi derrotado...", True, (220, 180, 180))
        score  = f_sub.render(f"Pontuacao: {self.total_score}", True, (220, 220, 100))

        cx = SCREEN_WIDTH  // 2
        cy = SCREEN_HEIGHT // 2

        surf.blit(titulo, (cx - titulo.get_width() // 2, cy - 130))
        surf.blit(sub,    (cx - sub.get_width()    // 2, cy - 30))
        surf.blit(score,  (cx - score.get_width()  // 2, cy + 10))

        # Recorde
        if self._novo_record:
            rec_txt = f_sub.render("NOVO RECORDE!", True, (255, 215, 0))
            surf.blit(rec_txt, (cx - rec_txt.get_width() // 2, cy + 46))
        else:
            rec_txt = f_hint.render(f"Recorde: {self._highscore}", True, (160, 160, 160))
            surf.blit(rec_txt, (cx - rec_txt.get_width() // 2, cy + 50))

        hint = f_hint.render("ENTER = menu principal", True, (160, 160, 160))
        surf.blit(hint, (cx - hint.get_width() // 2, cy + 90))

        screen.blit(surf, (0, 0))

    def render(self, screen: pygame.Surface):
        self.draw(screen)

    # -----------------------------------------------------------------------
    def _ir_para_menu(self):
        from meu_jogo.cenas.menu_scene import MenuScene
        player = self.manager.game.player
        player.hp = player.max_hp
        self.manager.game.state = GameState.MENU
        self.manager.scene_manager.change_scene(MenuScene(self.manager))
