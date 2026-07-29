# entities/player.py
import pygame

class Player:
    def __init__(self, animations: dict, x: int, y: int):
        self.animations = animations
        self.x = x
        self.y = y
        self.speed = 4
        self.direction = 0 # 0:Baixo, 1:Esq, 2:Dir, 3:Cima
        self.frame_index = 0
        self.image = self.animations[self.direction][self.frame_index]
        self.rect = self.image.get_rect(center=(self.x, self.y))

    def update(self, keys):
        moving = False
        
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.y -= self.speed
            self.direction = 3
            moving = True
        elif keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.y += self.speed
            self.direction = 0
            moving = True
        elif keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.x -= self.speed
            self.direction = 1
            moving = True
        elif keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.x += self.speed
            self.direction = 2
            moving = True

        # Atualiza a caixa de colisão
        self.rect.center = (self.x, self.y)

        # Animação super básica
        if moving:
            self.frame_index += 0.15 # Velocidade da animação
            if self.frame_index >= 4:
                self.frame_index = 0
        else:
            self.frame_index = 0

        self.image = self.animations[self.direction][int(self.frame_index)]

    def draw(self, surface):
        surface.blit(self.image, self.rect)