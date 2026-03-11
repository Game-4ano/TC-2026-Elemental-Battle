import pygame

class Tile:
    """
    Representa um único quadrado (tile) no mapa.
    """
    def __init__(self, name, element, color, is_walkable, damage_on_step=0):
        self.name = name
        self.element = element
        self.color = color
        self.is_walkable = is_walkable
        self.damage_on_step = damage_on_step

    def draw(self, surface, x, y, size, offset_x=0, offset_y=0):
        """
        Desenha o tile na superfície fornecida.
        """
        rect = pygame.Rect(x * size - offset_x, y * size - offset_y, size, size)
        pygame.draw.rect(surface, self.color, rect)
        # Desenha uma borda leve para distinguir os tiles
        pygame.draw.rect(surface, (40, 40, 40), rect, 1)

class Map:
    """
    Gere a grelha de tiles e a sua renderização.
    """
    def __init__(self, tile_matrix, tile_types, tile_size=32):
        self.matrix = tile_matrix
        self.tile_types = tile_types
        self.tile_size = tile_size
        self.width = len(tile_matrix[0]) if tile_matrix else 0
        self.height = len(tile_matrix)
        
        # Offset para a câmara (futura implementação)
        self.camera_offset_x = 0
        self.camera_offset_y = 0

    def get_tile_at(self, x, y):
        """
        Retorna o objeto Tile na posição (x, y) da matriz.
        """
        if 0 <= y < self.height and 0 <= x < self.width:
            tile_key = self.matrix[y][x]
            return self.tile_types.get(tile_key)
        return None

    def draw(self, surface):
        """
        Percorre a matriz e desenha cada tile.
        """
        for y in range(self.height):
            for x in range(self.width):
                tile = self.get_tile_at(x, y)
                if tile:
                    tile.draw(surface, x, y, self.tile_size, self.camera_offset_x, self.camera_offset_y)

    def set_camera_offset(self, x, y):
        """
        Define o offset da câmara para visualização.
        """
        self.camera_offset_x = x
        self.camera_offset_y = y

class GameMap:
    """
    Classe para compatibilidade com a estrutura antiga de dados de mapa.
    """
    def __init__(self, name, enemies, boss):
        self.name = name
        self.enemies = enemies
        self.boss = boss
