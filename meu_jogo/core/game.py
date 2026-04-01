import pygame
from entidades.player import Player
from cenas.mapa import Mapa

class Game:
    def __init__(self):
        pygame.init()

        self.tela = pygame.display.set_mode((1920,1080))
        pygame.display.set_caption("Elemental Battle")

        mapa_img = pygame.image.load("meu_jogo/assets/mapa/mapa.png")
        sprite_sheet = pygame.image.load("meu_jogo/assets/sprite/player.png")

        sprite_sheet = pygame.transform.scale(sprite_sheet, (128, 32))

        self.mapa = Mapa(mapa_img)
        self.player = Player(100, 100, sprite_sheet)

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