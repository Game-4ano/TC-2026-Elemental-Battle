import pygame

class Player:
    def __init__(self, x, y, sprite_sheet):
        self.x = x
        self.y = y
        self.velocidade = 5

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
        largura_total, altura_total = sprite_sheet.get_size()

        # sua sprite sheet: 4 colunas x 4 linhas
        colunas = 4
        linhas = 4

        largura = largura_total // colunas
        altura = altura_total // linhas

        escala = 2  # controla tamanho final

        direcoes = ["down", "left", "right", "up"]

        for linha, direcao in enumerate(direcoes):
            for coluna in range(colunas):
                frame = sprite_sheet.subsurface(
                    (coluna * largura, linha * altura, largura, altura)
                ).copy()  # IMPORTANTE

                frame = pygame.transform.scale(
                    frame, (largura * escala, altura * escala)
                )

                self.animacoes[direcao].append(frame)

    def mover(self, teclas):
        movimento = False

        if teclas[pygame.K_UP]:
            self.y -= self.velocidade
            self.direcao = "up"
            movimento = True

        elif teclas[pygame.K_DOWN]:
            self.y += self.velocidade
            self.direcao = "down"
            movimento = True

        elif teclas[pygame.K_LEFT]:
            self.x -= self.velocidade
            self.direcao = "left"
            movimento = True

        elif teclas[pygame.K_RIGHT]:
            self.x += self.velocidade
            self.direcao = "right"
            movimento = True

        if movimento:
            self.animar()
        else:
            self.frame_atual = 0

    def animar(self):
        self.tempo_animacao += 1

        if self.tempo_animacao >= 8:  
            self.frame_atual = (self.frame_atual + 1) % len(self.animacoes[self.direcao])
            self.tempo_animacao = 0

    def desenhar(self, tela):
        frame = self.animacoes[self.direcao][self.frame_atual]
        tela.blit(frame, (self.x, self.y))