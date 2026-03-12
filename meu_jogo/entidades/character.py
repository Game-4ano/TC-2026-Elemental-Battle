import pygame
from meu_jogo.core.config import (
    XP_PER_LEVEL,
    HP_LEVEL_INCREMENT,
    DAMAGE_LEVEL_INCREMENT,
    DEFENSE_LEVEL_INCREMENT,
    TILE_SIZE,
    MOVE_SPEED
)

class Character:
    def __init__(self, name, hp, damage, defense, element, weakness, is_boss=False):
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.damage = damage
        self.defense = defense
        self.element = element
        self.weakness = weakness
        self.level = 1
        self.xp = 0
        self.is_boss = is_boss

    def is_alive(self):
        return self.hp > 0

    def take_damage(self, amount):
        real_damage = max(amount - self.defense, 0)
        self.hp -= real_damage
        self.hp = max(0, self.hp)
        return real_damage

    def move(self, dx, dy, game_map):
        """
        Move o personagem no grid se o destino for atravessável.
        """
        new_x = self.grid_x + dx
        new_y = self.grid_y + dy

        if game_map.is_walkable(new_x, new_y):
            self.grid_x = new_x
            self.grid_y = new_y
            self.target_pixel_x = self.grid_x * TILE_SIZE
            self.target_pixel_y = self.grid_y * TILE_SIZE
            
            # Aciona o evento do tile ao entrar nele
            tile = game_map.get_tile_at(self.grid_x, self.grid_y)
            if tile:
                tile.on_step(self)
            return True
        return False

    def update(self):
        """
        Suaviza a transição entre tiles usando interpolação linear (Lerp).
        """
        # Interpolação simples para movimento suave
        self.pixel_x += (self.target_pixel_x - self.pixel_x) * MOVE_SPEED
        self.pixel_y += (self.target_pixel_y - self.pixel_y) * MOVE_SPEED

    def draw(self, surface, offset_x, offset_y):
        """
        Desenha o personagem na tela considerando o offset da câmara.
        """
        # Desenha um círculo colorido representando o personagem
        color = (255, 255, 0) # Amarelo para o herói
        pos = (int(self.pixel_x - offset_x + TILE_SIZE // 2), 
               int(self.pixel_y - offset_y + TILE_SIZE // 2))
        pygame.draw.circle(surface, color, pos, TILE_SIZE // 3)
        
        # Desenha uma borda
        pygame.draw.circle(surface, (0, 0, 0), pos, TILE_SIZE // 3, 2)

    def attack(self, target, damage_calculator):
        damage = damage_calculator(self, target)
        return target.take_damage(damage)

    def gain_xp(self, amount):
        self.xp += amount
        while self.xp >= XP_PER_LEVEL:
            self.xp -= XP_PER_LEVEL
            self.level_up()

    def level_up(self):
        self.level += 1
        self.max_hp += HP_LEVEL_INCREMENT
        self.damage += DAMAGE_LEVEL_INCREMENT
        self.defense += DEFENSE_LEVEL_INCREMENT
        self.hp = self.max_hp
        print(f"{self.name} subiu para o nível {self.level}!")
