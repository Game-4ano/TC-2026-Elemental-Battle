

import pygame

from .settings import LARGURA_TELA, ALTURA_TELA, FPS

class AssetsManager:
    @staticmethod
    def load_player_spritesheet(filepath: str, frame_w: int = 48, frame_h: int = 48):
        sheet = pygame.image.load(filepath).convert()
        sheet.set_colorkey((255, 255, 255))

        total_w, total_h = sheet.get_size()
        sub_w = total_w // 4
        sub_h = total_h // 4

        animations = {0: [], 1: [], 2: [], 3: []}

        for row in range(4):
            for col in range(4):
                rect = pygame.Rect(col * sub_w, row * sub_h, sub_w, sub_h)
                frame = sheet.subsurface(rect).copy()
                scaled_frame = pygame.transform.scale(frame, (frame_w, frame_h))
                animations[row].append(scaled_frame)

        return animations
    
    @staticmethod
    def load_background(filepath: str) -> pygame.Surface:
        bg = pygame.image.load(filepath).convert()
        return pygame.transform.scale(bg, (LARGURA_TELA, ALTURA_TELA))


AssetManager = AssetsManager