import pygame
from abc import ABC, abstractmethod


class GameObject(ABC):
    """
    Classe abstrata base para todos os objetos do jogo.
    Usa pygame.Vector2 para posição e velocidade (física real com dt).
    """

    def __init__(self, x: float, y: float):
        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0.0, 0.0)
        self.alive = True

    def apply_physics(self, dt: float):
        """Fórmula: posição += velocidade * tempo"""
        self.position += self.velocity * dt

    @abstractmethod
    def update(self, dt: float):
        pass

    @abstractmethod
    def draw(self, screen: pygame.Surface):
        pass