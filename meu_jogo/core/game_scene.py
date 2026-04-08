import pygame
from abc import ABC, abstractmethod


class GameScene(ABC):
    """
    Interface genérica para todas as cenas do jogo
    (mundos, menus, batalhas, etc.).
    """

    def __init__(self, manager):
        self.manager = manager

    @abstractmethod
    def handle_event(self, event: pygame.event.Event):
        pass

    @abstractmethod
    def update(self, dt: float):
        pass

    @abstractmethod
    def draw(self, screen: pygame.Surface):
        pass