import pygame
from meu_jogo.core.config import TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT

class Tile:
    """
    Classe base para um quadrado (tile) no mapa.
    """
    def __init__(self, name, element, color, is_walkable, damage_on_step=0):
        self.name = name
        self.element = element
        self.color = color
        self.is_walkable = is_walkable
        self.damage_on_step = damage_on_step

    def on_step(self, player):
        """
        Método chamado quando o jogador pisa no tile.
        Pode ser sobrescrito por subclasses para efeitos específicos (Polimorfismo).
        """
        if self.damage_on_step > 0:
            player.take_damage(self.damage_on_step)
            print(f"O jogador pisou em {self.name} ({self.element}) e recebeu {self.damage_on_step} de dano!")

    def draw(self, surface, x, y, size, offset_x=0, offset_y=0):
        """
        Desenha o tile na superfície fornecida considerando o offset da câmara.
        """
        rect = pygame.Rect(x * size - offset_x, y * size - offset_y, size, size)
        pygame.draw.rect(surface, self.color, rect)
        # Desenha uma borda leve para distinguir os tiles
        pygame.draw.rect(surface, (40, 40, 40), rect, 1)

# --- Subclasses de Tile (Polimorfismo) ---

class WaterTile(Tile):
    def __init__(self, name="Água", color=(30, 144, 255), damage=5):
        super().__init__(name, "Water", color, True, damage)

    def on_step(self, player):
        # Exemplo de polimorfismo: se o jogador for de Fogo, recebe dano dobrado na água
        damage = self.damage_on_step
        if player.element == "Fire":
            damage *= 2
            print("Dano elemental crítico! Fogo vs Água.")
        player.take_damage(damage)

class FireTile(Tile):
    def __init__(self, name="Brasa", color=(255, 69, 0), damage=10):
        super().__init__(name, "Fire", color, True, damage)

    def on_step(self, player):
        # Se o jogador for de Planta (Grass), recebe mais dano no fogo
        damage = self.damage_on_step
        if player.element == "Grass":
            damage *= 2
            print("Dano elemental crítico! Planta vs Fogo.")
        player.take_damage(damage)

class GrassTile(Tile):
    def __init__(self, name="Grama", color=(34, 139, 34)):
        super().__init__(name, "Grass", color, True, 0)

class WindTile(Tile):
    def __init__(self, name="Vento", color=(173, 216, 230)):
        super().__init__(name, "Air", color, True, 0)

class WallTile(Tile):
    def __init__(self, name="Montanha", color=(139, 69, 19)):
        super().__init__(name, "None", color, False, 0)

# --- Classe Map ---

class Map:
    """
    Gere a grelha de tiles, a renderização e a câmara.
    """
    def __init__(self, tile_matrix, tile_types, tile_size=TILE_SIZE):
        self.matrix = tile_matrix
        self.tile_types = tile_types
        self.tile_size = tile_size
        self.width = len(tile_matrix[0]) if tile_matrix else 0
        self.height = len(tile_matrix)
        
        # Offset para a câmara
        self.camera_offset_x = 0
        self.camera_offset_y = 0

    def get_tile_at(self, grid_x, grid_y):
        """
        Retorna o objeto Tile na posição (grid_x, grid_y) da matriz.
        """
        if 0 <= grid_y < self.height and 0 <= grid_x < self.width:
            tile_key = self.matrix[grid_y][grid_x]
            return self.tile_types.get(tile_key)
        return None

    def is_walkable(self, grid_x, grid_y):
        """
        Verifica se o tile na posição é atravessável.
        """
        tile = self.get_tile_at(grid_x, grid_y)
        return tile.is_walkable if tile else False

    def update_camera(self, player_pixel_x, player_pixel_y):
        """
        Faz a câmara seguir o jogador, centralizando-o na tela.
        """
        self.camera_offset_x = player_pixel_x - SCREEN_WIDTH // 2
        self.camera_offset_y = player_pixel_y - SCREEN_HEIGHT // 2
        
        # Limitar a câmara às bordas do mapa
        self.camera_offset_x = max(0, min(self.camera_offset_x, self.width * self.tile_size - SCREEN_WIDTH))
        self.camera_offset_y = max(0, min(self.camera_offset_y, self.height * self.tile_size - SCREEN_HEIGHT))

    def draw(self, surface):
        """
        Percorre a matriz e desenha cada tile visível.
        """
        for y in range(self.height):
            for x in range(self.width):
                tile = self.get_tile_at(x, y)
                if tile:
                    tile.draw(surface, x, y, self.tile_size, self.camera_offset_x, self.camera_offset_y)

class GameMap:
    """
    Classe para compatibilidade com a estrutura antiga de dados de mapa.
    """
    def __init__(self, name, enemies, boss):
        self.name = name
        self.enemies = enemies
        self.boss = boss
