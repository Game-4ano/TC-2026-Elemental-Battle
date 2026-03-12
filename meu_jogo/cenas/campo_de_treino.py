import math
import pygame

from meu_jogo.cenas.base_cenas import BaseScene
from meu_jogo.cenas.battle_scene import BattleScene
from meu_jogo.core.config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    GREEN,
    DARK_GREEN,
    BROWN,
    YELLOW,
    BLACK,
    WHITE,
)


class CampoDeTreinoScene(BaseScene):
    def __init__(self, manager):
        super().__init__(manager)
        self.font = pygame.font.SysFont(None, 24)
        self.big_font = pygame.font.SysFont(None, 30)

        self.center_x = SCREEN_WIDTH // 2
        self.center_y = SCREEN_HEIGHT // 2
        self.tree_radius = 210

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                battle = self.manager.game.start_game()
                self.manager.scene_manager.change_scene(BattleScene(self.manager, battle))

    def update(self, dt):
        pass

    def render(self, screen):
        screen.fill(GREEN)

        # árvores em círculo
        for i in range(14):
            angle = (2 * math.pi / 14) * i
            x = int(self.center_x + math.cos(angle) * self.tree_radius)
            y = int(self.center_y + math.sin(angle) * self.tree_radius)

            pygame.draw.circle(screen, BROWN, (x, y + 10), 10)
            pygame.draw.circle(screen, DARK_GREEN, (x, y), 22)

        # espantalho
        scare_x = self.center_x
        scare_y = self.center_y

        pygame.draw.circle(screen, YELLOW, (scare_x, scare_y - 35), 14)
        pygame.draw.line(screen, BROWN, (scare_x, scare_y - 20), (scare_x, scare_y + 35), 4)
        pygame.draw.line(screen, BROWN, (scare_x - 25, scare_y), (scare_x + 25, scare_y), 4)
        pygame.draw.line(screen, BROWN, (scare_x, scare_y + 35), (scare_x - 15, scare_y + 60), 4)
        pygame.draw.line(screen, BROWN, (scare_x, scare_y + 35), (scare_x + 15, scare_y + 60), 4)

        title = self.big_font.render("Campo de Treino", True, BLACK)
        tip1 = self.font.render("Pressione ESPAÇO para iniciar a batalha", True, WHITE)
        tip2 = self.font.render("Primeira criatura: elemento Fogo", True, WHITE)

        screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 30))
        screen.blit(tip1, (SCREEN_WIDTH // 2 - tip1.get_width() // 2, 430))
        screen.blit(tip2, (SCREEN_WIDTH // 2 - tip2.get_width() // 2, 455))