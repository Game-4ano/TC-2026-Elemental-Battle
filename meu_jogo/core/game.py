<<<<<<< HEAD
import pygame
from meu_jogo.entidades.player import Player
from meu_jogo.cenas.mapa import Mapa
=======
"""
Controla fluxo geral do jogo.
"""

from meu_jogo.core.battle import Battle
from meu_jogo.entidades.ai_entidade import BasicAI
from meu_jogo.core.game_state import GameState
from meu_jogo.core.config import DEFAULT_XP_REWARD, BOSS_XP_REWARD

>>>>>>> main

class Game:
    def __init__(self):
        pygame.init()

<<<<<<< HEAD
        self.tela = pygame.display.set_mode((1920, 1080))
        pygame.display.set_caption("Elemental Battle")
=======
    def __init__(self, player, maps):
        self.player = player
        self.maps = maps
        self.current_map_index = 0
        self.current_enemy_index = 0
        self.state = GameState.TRAINING
>>>>>>> main

        mapa_img = pygame.image.load("meu_jogo/assets/mapa/mapa.png")
        sprite_sheet = pygame.image.load("meu_jogo/assets/sprite/player.png")


        self.mapa = Mapa(mapa_img)
        self.player = Player(10, 10, sprite_sheet)

        self.rodando = True

    def run(self):
        while self.rodando:
            pygame.time.delay(50)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.rodando = False

            teclas = pygame.key.get_pressed()
            self.player.mover(teclas)

            self.mapa.desenhar(self.tela)
            self.player.desenhar(self.tela)

            pygame.display.update()

        pygame.quit()