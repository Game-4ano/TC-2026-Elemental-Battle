import pygame

class Player:
    def __init__(self, x, y, sprite_sheet):
        self.x = x
        self.y = y

        self.animacoes = {
            "down": [],
            "left": [],
            "right": [],
            "up": []
        }

        self.direcao = "down"
        self.frame_atual = 0
        self.tempo_animacao = 0

        self.carregar_sprites(sprite_sheet)

    def carregar_sprites(self, sprite_sheet):
        largura_sprite = 32
        altura_sprite = 32

        sprites = []

        # Carrega os 4 frames da imagem (1 linha)
        for i in range(4):
            frame = sprite_sheet.subsurface(
                (i * largura_sprite, 0, largura_sprite, altura_sprite)
            )
            sprites.append(frame)

        
        self.animacoes["down"] = sprites
        self.animacoes["up"] = sprites
        self.animacoes["left"] = sprites
        self.animacoes["right"] = sprites

    def mover(self, teclas):
        movimento = False

        if teclas[pygame.K_UP]:
            self.y -= 5
            self.direcao = "up"
            movimento = True

        elif teclas[pygame.K_DOWN]:
            self.y += 5
            self.direcao = "down"
            movimento = True

        elif teclas[pygame.K_LEFT]:
            self.x -= 5
            self.direcao = "left"
            movimento = True

        elif teclas[pygame.K_RIGHT]:
            self.x += 5
            self.direcao = "right"
            movimento = True

        if movimento:
            self.animar()
        else:
            self.frame_atual = 0

    def animar(self):
        self.tempo_animacao += 1

        if self.tempo_animacao >= 10:
            self.frame_atual = (self.frame_atual + 1) % len(self.animacoes[self.direcao])
            self.tempo_animacao = 0

    def desenhar(self, tela):
        frame = self.animacoes[self.direcao][self.frame_atual]
        tela.blit(frame, (self.x, self.y))