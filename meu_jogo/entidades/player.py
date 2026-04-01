# entidades/player.py
import pygame

class Player:
    def __init__(self, x, y, sprite_sheet):
        self.x = x
        self.y = y

        self.frames = []
        self.frame_atual = 0
        self.tempo_animacao = 0

        self.carregar_sprites(sprite_sheet)

    def carregar_sprites(self, sprite_sheet):
        largura_frame = 32
        altura_frame = 32
        escala = 6

        for i in range(4):  # 4 frames
            frame = sprite_sheet.subsurface((i * largura_frame, 0, largura_frame, altura_frame))
            frame = pygame.transform.scale(frame, (largura_frame * escala, altura_frame * escala))
            self.frames.append(frame)

    def mover(self, teclas):
        if teclas[pygame.K_RIGHT]:
            self.x += 5
            self.animar()
        elif teclas[pygame.K_LEFT]:
            self.x -= 5
            self.animar()

    def animar(self):
        self.tempo_animacao += 1

        if self.tempo_animacao >= 10:
            self.frame_atual = (self.frame_atual + 1) % len(self.frames)
            self.tempo_animacao = 0

    def desenhar(self, tela):
        tela.blit(self.frames[self.frame_atual], (self.x, self.y))