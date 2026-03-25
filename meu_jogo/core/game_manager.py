import pygame

from meu_jogo.core.config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE
from meu_jogo.core.scene_manager import SceneManager
from meu_jogo.cenas.campo_de_treino import CampoDeTreinoScene


class GameManager:
    def __init__(self, game, map_manager, player):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True

        self.game = game
        self.map_manager = map_manager
        self.player = player
        self.scene_manager = SceneManager()
        self.scene_manager.change_scene(CampoDeTreinoScene(self))

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                else:
                    self.scene_manager.handle_event(event)

            # Processa troca de mapa se houver portal ativado
            self.map_manager.process_map_change(self.player)

            self.scene_manager.update(dt)
            self.scene_manager.render(self.screen)
            pygame.display.flip()

        pygame.quit()