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
    """
    Classe base para personagens (Jogador e Inimigos).
    Implementa mecânicas de movimento por grid, vida e atributos elementais.
    """
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
        self.is_defending = False

        # Atributos de posição no grid
        self.grid_x = 1
        self.grid_y = 1
        
        # Atributos para movimento suave (interpolação)
        self.pixel_x = self.grid_x * TILE_SIZE
        self.pixel_y = self.grid_y * TILE_SIZE
        self.target_pixel_x = self.pixel_x
        self.target_pixel_y = self.pixel_y

    def is_alive(self):
        return self.hp > 0

    def take_damage(self, amount):
        """
        Aplica dano ao personagem considerando a defesa.
        Dano mínimo de 1 se o valor base for maior que 0.
        """
        real_damage = max(amount - self.defense, 1) if amount > 0 else 0

        if self.is_defending:
            real_damage = int(real_damage * 0.5)
            self.is_defending = False  

        self.hp -= real_damage
        self.hp = max(0, self.hp)
        return real_damage

    def move(self, dx, dy, game_map, map_manager=None):
        """
        Move o personagem no grid se o destino for atravessável.
        Aciona eventos de tile (dano, portais).
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
                tile.on_step(self, map_manager)
            return True
        return False

    def update(self):
        """
        Atualiza a posição visual do personagem usando interpolação linear (Lerp).
        """
        self.pixel_x += (self.target_pixel_x - self.pixel_x) * MOVE_SPEED
        self.pixel_y += (self.target_pixel_y - self.pixel_y) * MOVE_SPEED

    def draw(self, surface, offset_x, offset_y):
        """
        Desenha o personagem na tela. Temporariamente representado por um círculo.
        """
        color = (255, 255, 0) # Amarelo para o herói
        pos = (int(self.pixel_x - offset_x + TILE_SIZE // 2), 
               int(self.pixel_y - offset_y + TILE_SIZE // 2))
        pygame.draw.circle(surface, color, pos, TILE_SIZE // 3)
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
