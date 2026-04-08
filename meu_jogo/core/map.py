import pygame
from meu_jogo.core.config import TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT


class Stage:
    def __init__(self, name):
        self.name = name

    def update(self): pass
    def draw(self, surface): pass


# ---------------------------------------------------------------------------
# Tiles
# ---------------------------------------------------------------------------
class Tile:
    def __init__(self, name, element, color, is_walkable, damage_on_step=0):
        self.name           = name
        self.element        = element
        self.color          = color
        self.is_walkable    = is_walkable
        self.damage_on_step = damage_on_step

    def on_step(self, player, map_manager=None):
        if self.damage_on_step > 0:
            player.take_damage(self.damage_on_step)

    def draw(self, surface, x, y, size, offset_x=0, offset_y=0):
        rect = pygame.Rect(x * size - offset_x, y * size - offset_y, size, size)
        pygame.draw.rect(surface, self.color, rect)
        # Borda sutil
        border = tuple(max(c - 30, 0) for c in self.color)
        pygame.draw.rect(surface, border, rect, 1)


class WaterTile(Tile):
    def __init__(self, name="Poça", color=(30, 100, 200), damage=5):
        super().__init__(name, "Water", color, True, damage)

    def on_step(self, player, map_manager=None):
        dmg = self.damage_on_step * (2 if getattr(player, "element", "") == "Fire" else 1)
        player.take_damage(dmg)

    def draw(self, surface, x, y, size, offset_x=0, offset_y=0):
        rect = pygame.Rect(x * size - offset_x, y * size - offset_y, size, size)
        pygame.draw.rect(surface, self.color, rect)
        # Reflexo de água
        lighter = (min(self.color[0]+40,255), min(self.color[1]+40,255), min(self.color[2]+50,255))
        wave_y  = rect.y + size // 3
        pygame.draw.line(surface, lighter, (rect.x+3, wave_y), (rect.x + size//2, wave_y), 1)
        pygame.draw.rect(surface, (0, 60, 140), rect, 1)


class FireTile(Tile):
    def __init__(self, name="Brasa", color=(200, 60, 0), damage=10):
        super().__init__(name, "Fire", color, True, damage)

    def on_step(self, player, map_manager=None):
        dmg = self.damage_on_step * (2 if getattr(player, "element", "") == "Grass" else 1)
        player.take_damage(dmg)

    def draw(self, surface, x, y, size, offset_x=0, offset_y=0):
        rect = pygame.Rect(x * size - offset_x, y * size - offset_y, size, size)
        pygame.draw.rect(surface, self.color, rect)
        # Brilho no centro
        cx, cy = rect.centerx, rect.centery
        pygame.draw.circle(surface, (240, 140, 0), (cx, cy), size // 5)
        pygame.draw.rect(surface, (140, 30, 0), rect, 1)


class GrassTile(Tile):
    def __init__(self, name="Grama", color=(55, 140, 55)):
        super().__init__(name, "Grass", color, True, 0)

    def draw(self, surface, x, y, size, offset_x=0, offset_y=0):
        rect = pygame.Rect(x * size - offset_x, y * size - offset_y, size, size)
        pygame.draw.rect(surface, self.color, rect)
        # Textura de grama — riscos verticais sutis
        stripe = (max(self.color[0]-15,0), min(self.color[1]+20,255), max(self.color[2]-10,0))
        for i in range(3):
            sx = rect.x + size // 4 * (i + 1)
            pygame.draw.line(surface, stripe, (sx, rect.y+4), (sx, rect.y+size-4), 1)
        pygame.draw.rect(surface, (30, 100, 30), rect, 1)


class WindTile(Tile):
    def __init__(self, name="Vento", color=(140, 195, 220)):
        super().__init__(name, "Air", color, True, 0)

    def draw(self, surface, x, y, size, offset_x=0, offset_y=0):
        rect = pygame.Rect(x * size - offset_x, y * size - offset_y, size, size)
        pygame.draw.rect(surface, self.color, rect)
        # Linhas curvas simulando vento
        lighter = (min(self.color[0]+30,255), min(self.color[1]+20,255), 255)
        for i in range(2):
            wy = rect.y + size // 3 * (i + 1)
            pygame.draw.line(surface, lighter, (rect.x+2, wy), (rect.x+size-2, wy), 1)
        pygame.draw.rect(surface, (90, 150, 190), rect, 1)


class WallTile(Tile):
    def __init__(self, name="Montanha", color=(90, 60, 30)):
        super().__init__(name, "None", color, False, 0)

    def draw(self, surface, x, y, size, offset_x=0, offset_y=0):
        rect = pygame.Rect(x * size - offset_x, y * size - offset_y, size, size)
        pygame.draw.rect(surface, self.color, rect)
        # Sombra superior para dar volume
        top_color = (min(self.color[0]+30,255), min(self.color[1]+20,255), min(self.color[2]+10,255))
        top_rect  = pygame.Rect(rect.x, rect.y, rect.w, rect.h // 3)
        pygame.draw.rect(surface, top_color, top_rect)
        pygame.draw.rect(surface, (40, 25, 10), rect, 1)


class PortalTile(Tile):
    def __init__(self, name, color, destination_map_name, spawn_x, spawn_y):
        super().__init__(name, "None", color, True, 0)
        self.destination_map_name = destination_map_name
        self.spawn_x = spawn_x
        self.spawn_y = spawn_y

    def on_step(self, player, map_manager):
        if map_manager:
            map_manager.request_map_change(
                self.destination_map_name, self.spawn_x, self.spawn_y
            )

    def draw(self, surface, x, y, size, offset_x=0, offset_y=0):
        rect = pygame.Rect(x * size - offset_x, y * size - offset_y, size, size)
        pygame.draw.rect(surface, self.color, rect)
        # Brilho pulsante simulado — borda mais clara
        bright = tuple(min(c + 70, 255) for c in self.color)
        pygame.draw.rect(surface, bright, rect.inflate(-6, -6), 2)
        pygame.draw.rect(surface, (255, 255, 255), rect, 1)


# ---------------------------------------------------------------------------
# Map (Stage baseado em tiles) — com suporte a imagem de fundo
# ---------------------------------------------------------------------------
class Map(Stage):
    def __init__(self, name, tile_matrix, tile_types,
                 tile_size=TILE_SIZE, bg_image: pygame.Surface | None = None):
        super().__init__(name)
        self.matrix      = tile_matrix
        self.tile_types  = tile_types
        self.tile_size   = tile_size
        self.width       = len(tile_matrix[0]) if tile_matrix else 0
        self.height      = len(tile_matrix)
        self.camera_offset_x = 0
        self.camera_offset_y = 0
        self.bg_image    = bg_image   # pygame.Surface opcional

    def get_tile_at(self, grid_x, grid_y):
        if 0 <= grid_y < self.height and 0 <= grid_x < self.width:
            return self.tile_types.get(self.matrix[grid_y][grid_x])
        return None

    def is_walkable(self, grid_x, grid_y):
        tile = self.get_tile_at(grid_x, grid_y)
        return tile.is_walkable if tile else False

    def update_camera(self, player_pixel_x, player_pixel_y):
        target_x = player_pixel_x - SCREEN_WIDTH  // 2
        target_y = player_pixel_y - SCREEN_HEIGHT // 2
        max_x = self.width  * self.tile_size - SCREEN_WIDTH
        max_y = self.height * self.tile_size - SCREEN_HEIGHT
        self.camera_offset_x = max(0, min(target_x, max(max_x, 0)))
        self.camera_offset_y = max(0, min(target_y, max(max_y, 0)))

    def draw(self, surface: pygame.Surface):
        # 1) Imagem de fundo (esticada para preencher a tela)
        if self.bg_image:
            scaled = pygame.transform.scale(self.bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
            surface.blit(scaled, (0, 0))

        # 2) Tiles por cima com transparência (alpha 180)
        tile_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        for y in range(self.height):
            for x in range(self.width):
                tile = self.get_tile_at(x, y)
                if tile:
                    tile.draw(tile_surface, x, y, self.tile_size,
                              self.camera_offset_x, self.camera_offset_y)
        surface.blit(tile_surface, (0, 0))


# ---------------------------------------------------------------------------
# MapManager
# ---------------------------------------------------------------------------
class MapManager:
    def __init__(self, initial_map_name, all_map_data,
                 bg_image: pygame.Surface | None = None):
        self.all_map_data    = all_map_data
        self.bg_image        = bg_image
        self.current_map_name = initial_map_name
        self.current_map     = None
        self.maps_cache      = {}
        self.pending_map_change = None
        self.load_map(initial_map_name)

    def load_map(self, map_name):
        if map_name not in self.maps_cache:
            data = self.all_map_data.get(map_name)
            if not data:
                raise ValueError(f"Mapa '{map_name}' não encontrado.")
            self.maps_cache[map_name] = Map(
                map_name, data["matrix"], data["tile_types"],
                bg_image=self.bg_image,
            )
        self.current_map      = self.maps_cache[map_name]
        self.current_map_name = map_name

    def request_map_change(self, dest, spawn_x, spawn_y):
        self.pending_map_change = (dest, spawn_x, spawn_y)

    def process_map_change(self, player):
        if self.pending_map_change:
            dest, sx, sy = self.pending_map_change
            self.load_map(dest)
            player.grid_x       = sx
            player.grid_y       = sy
            player.pixel_x      = sx * TILE_SIZE
            player.pixel_y      = sy * TILE_SIZE
            player.target_pixel_x = player.pixel_x
            player.target_pixel_y = player.pixel_y
            self.pending_map_change = None
            return True
        return False


class GameMap:
    """Compatibilidade com a estrutura antiga."""
    def __init__(self, name, enemies, boss):
        self.name    = name
        self.enemies = enemies
        self.boss    = boss