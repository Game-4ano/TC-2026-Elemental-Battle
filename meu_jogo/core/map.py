import pygame
from meu_jogo.core.config import TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT

# --- Base Stage Class for Polymorphism ---
class Stage:
    """
    Classe base para diferentes tipos de cenários (stages) no jogo.
    Permite polimorfismo para cenários com lógicas específicas (ex: BattleRoom, ForestRoom).
    """
    def __init__(self, name):
        self.name = name

    def update(self):
        """
        Atualiza a lógica do cenário (inimigos, eventos, etc.).
        """
        pass

    def draw(self, surface):
        """
        Desenha o cenário na superfície fornecida.
        """
        pass

# --- Tile Classes ---
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

    def on_step(self, player, map_manager=None):
        """
        Método chamado quando o jogador pisa no tile.
        Pode ser sobrescrito por subclasses para efeitos específicos (Polimorfismo).
        """
        if self.damage_on_step > 0:
            player.take_damage(self.damage_on_step)
            # print(f"O jogador pisou em {self.name} ({self.element}) e recebeu {self.damage_on_step} de dano!")

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
    def __init__(self, name="Poça", color=(30, 144, 255), damage=5):
        super().__init__(name, "Water", color, True, damage)

    def on_step(self, player, map_manager=None):
        damage = self.damage_on_step
        if player.element == "Fire":
            damage *= 2
            # print("Dano elemental crítico! Fogo vs Água.")
        player.take_damage(damage)

class FireTile(Tile):
    def __init__(self, name="Brasa", color=(255, 69, 0), damage=10):
        super().__init__(name, "Fire", color, True, damage)

    def on_step(self, player, map_manager=None):
        damage = self.damage_on_step
        if player.element == "Grass":
            damage *= 2
            # print("Dano elemental crítico! Planta vs Fogo.")
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

class PortalTile(Tile):
    """
    Tile especial que aciona uma transição para outro mapa.
    """
    def __init__(self, name, color, destination_map_name, spawn_x, spawn_y):
        super().__init__(name, "None", color, True, 0)
        self.destination_map_name = destination_map_name
        self.spawn_x = spawn_x
        self.spawn_y = spawn_y

    def on_step(self, player, map_manager):
        if map_manager:
            map_manager.request_map_change(self.destination_map_name, self.spawn_x, self.spawn_y)

# --- Classe Map (agora um tipo de Stage) ---

class Map(Stage):
    """
    Gere a grelha de tiles, a renderização e a câmara para um cenário específico.
    """
    def __init__(self, name, tile_matrix, tile_types, tile_size=TILE_SIZE):
        super().__init__(name)
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
        Faz a câmara seguir o jogador, centralizando-o na tela, mas travando nas bordas do mapa.
        """
        # Posição desejada da câmara para centralizar o jogador
        target_camera_x = player_pixel_x - SCREEN_WIDTH // 2
        target_camera_y = player_pixel_y - SCREEN_HEIGHT // 2
        
        # Limitar a câmara às bordas do mapa
        max_camera_x = self.width * self.tile_size - SCREEN_WIDTH
        max_camera_y = self.height * self.tile_size - SCREEN_HEIGHT

        self.camera_offset_x = max(0, min(target_camera_x, max_camera_x))
        self.camera_offset_y = max(0, min(target_camera_y, max_camera_y))

        # Se o mapa for menor que a tela, centraliza o mapa
        if self.width * self.tile_size < SCREEN_WIDTH:
            self.camera_offset_x = (self.width * self.tile_size - SCREEN_WIDTH) // 2
        if self.height * self.tile_size < SCREEN_HEIGHT:
            self.camera_offset_y = (self.height * self.tile_size - SCREEN_HEIGHT) // 2

    def draw(self, surface):
        """
        Percorre a matriz e desenha cada tile visível.
        """
        for y in range(self.height):
            for x in range(self.width):
                tile = self.get_tile_at(x, y)
                if tile:
                    tile.draw(surface, x, y, self.tile_size, self.camera_offset_x, self.camera_offset_y)

# --- MapManager Class ---
class MapManager:
    """
    Gerencia o carregamento e a transição entre diferentes mapas/cenários.
    """
    def __init__(self, initial_map_name, all_map_data):
        self.all_map_data = all_map_data # Dicionário com dados brutos dos mapas
        self.current_map_name = initial_map_name
        self.current_map = None
        self.maps_cache = {}
        self.pending_map_change = None # (destination_map_name, spawn_x, spawn_y)
        self.load_map(initial_map_name)

    def load_map(self, map_name):
        """
        Carrega um mapa pelo nome, usando cache se já carregado.
        """
        if map_name not in self.maps_cache:
            map_data = self.all_map_data.get(map_name)
            if not map_data:
                raise ValueError(f"Mapa \'{map_name}\' não encontrado nos dados.")
            
            # Aqui, \'Map\' é a nossa implementação de Stage para mapas baseados em tiles
            self.maps_cache[map_name] = Map(map_name, map_data["matrix"], map_data["tile_types"])
        
        self.current_map = self.maps_cache[map_name]
        self.current_map_name = map_name
        print(f"Mapa carregado: {map_name}")

    def request_map_change(self, destination_map_name, spawn_x, spawn_y):
        """
        Solicita uma mudança de mapa para o próximo frame do jogo.
        """
        self.pending_map_change = (destination_map_name, spawn_x, spawn_y)

    def process_map_change(self, player):
        """
        Executa a mudança de mapa pendente e reposiciona o jogador.
        Retorna True se houve mudança, False caso contrário.
        """
        if self.pending_map_change:
            dest_map_name, spawn_x, spawn_y = self.pending_map_change
            self.load_map(dest_map_name)
            player.grid_x = spawn_x
            player.grid_y = spawn_y
            player.pixel_x = spawn_x * TILE_SIZE
            player.pixel_y = spawn_y * TILE_SIZE
            player.target_pixel_x = player.pixel_x
            player.target_pixel_y = player.pixel_y
            self.pending_map_change = None
            return True
        return False


class GameMap:
    """
    Classe para compatibilidade com a estrutura antiga de dados de mapa.
    """
    def __init__(self, name, enemies, boss):
        self.name = name
        self.enemies = enemies
        self.boss = boss
