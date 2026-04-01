import pygame
class Mapa:
    def __init__(self, imagem):
        self.imagem = imagem

    def desenhar(self, tela):
        tela.blit(self.imagem, (0, 0))