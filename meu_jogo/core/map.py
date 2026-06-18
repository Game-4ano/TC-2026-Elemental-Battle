import pygame
from meu_jogo.core.config import TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT
from meu_jogo.midia.sprites.sprite_factory import get_scene_image


class Stage:
    def __init__(self, name):
        self.name = name

    def update(self): pass
    def draw(self, surface): pass


# ---------------------------------------------------------------------------
# Tiles
# ---------------------------------------------------------------------------
class Tile:
    # Subclasses que possuem pixel art em tile_sprites.py definem esta chave.
    # None = sem sprite, usa draw por primitivas como fallback.
    tile_sprite_key: str | None = None
    tile_sprite_fps: float = 2.0   # frames por segundo para tiles animados

    def __init__(self, name, element, color, is_walkable, damage_on_step=0):
        self.name           = name
        self.element        = element
        self.color          = color
        self.is_walkable    = is_walkable
        self.damage_on_step = damage_on_step

    def on_step(self, player, map_manager=None):
        if self.damage_on_step > 0:
            player.take_damage(self.damage_on_step)

    def _try_draw_sprite(self, surface, x, y, size, offset_x, offset_y) -> bool:
        """Tenta desenhar sprite pixel art. Retorna True se sucesso."""
        if not self.tile_sprite_key:
            return False
        try:
            from meu_jogo.midia.sprites.tile_sprites import get_tile_sprite, get_tile_frame_count
            n = get_tile_frame_count(self.tile_sprite_key)
            if n == 0:
                return False
            frame = int(pygame.time.get_ticks() / (1000.0 / self.tile_sprite_fps)) % n
            spr = get_tile_sprite(self.tile_sprite_key, frame)
            if spr is None:
                return False
            rx = x * size - int(offset_x)
            ry = y * size - int(offset_y)
            if spr.get_width() != size or spr.get_height() != size:
                spr = pygame.transform.scale(spr, (size, size))
            surface.blit(spr, (rx, ry))
            return True
        except Exception:
            return False

    def draw(self, surface, x, y, size, offset_x=0, offset_y=0):
        if self._try_draw_sprite(surface, x, y, size, offset_x, offset_y):
            return
        rect = pygame.Rect(x * size - int(offset_x), y * size - int(offset_y), size, size)
        pygame.draw.rect(surface, self.color, rect)
        border = tuple(max(c - 30, 0) for c in self.color)
        pygame.draw.rect(surface, border, rect, 1)


class WaterTile(Tile):
    tile_sprite_key = "water"
    tile_sprite_fps = 1.5

    def __init__(self, name="Poça", color=(30, 100, 200), damage=5):
        super().__init__(name, "Water", color, True, damage)

    def on_step(self, player, map_manager=None):
        dmg = self.damage_on_step * (2 if getattr(player, "element", "") == "Fire" else 1)
        player.take_damage(dmg)

    def draw(self, surface, x, y, size, offset_x=0, offset_y=0):
        if self._try_draw_sprite(surface, x, y, size, offset_x, offset_y):
            return
        rect = pygame.Rect(x * size - int(offset_x), y * size - int(offset_y), size, size)
        pygame.draw.rect(surface, self.color, rect)
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
    tile_sprite_key = "grass"

    def __init__(self, name="Grama", color=(55, 140, 55)):
        super().__init__(name, "Grass", color, True, 0)

    def draw(self, surface, x, y, size, offset_x=0, offset_y=0):
        if self._try_draw_sprite(surface, x, y, size, offset_x, offset_y):
            return
        rect = pygame.Rect(x * size - int(offset_x), y * size - int(offset_y), size, size)
        pygame.draw.rect(surface, self.color, rect)
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
    tile_sprite_key = "rock"

    def __init__(self, name="Montanha", color=(90, 60, 30)):
        super().__init__(name, "None", color, False, 0)

    def draw(self, surface, x, y, size, offset_x=0, offset_y=0):
        if self._try_draw_sprite(surface, x, y, size, offset_x, offset_y):
            return
        rect = pygame.Rect(x * size - int(offset_x), y * size - int(offset_y), size, size)
        pygame.draw.rect(surface, self.color, rect)
        top_color = (min(self.color[0]+30,255), min(self.color[1]+20,255), min(self.color[2]+10,255))
        top_rect  = pygame.Rect(rect.x, rect.y, rect.w, rect.h // 3)
        pygame.draw.rect(surface, top_color, top_rect)
        pygame.draw.rect(surface, (40, 25, 10), rect, 1)


# ---------------------------------------------------------------------------
# Tiles temáticos — Região Água (Oeste)
# ---------------------------------------------------------------------------
class IceTile(Tile):
    def __init__(self):
        super().__init__("Gelo", "Water", (180, 220, 240), True, 0)

    def draw(self, surface, x, y, size, offset_x=0, offset_y=0):
        rect = pygame.Rect(x * size - offset_x, y * size - offset_y, size, size)
        pygame.draw.rect(surface, self.color, rect)
        t = (pygame.time.get_ticks() % 2000) / 2000.0
        import math
        brilho = int(200 + 55 * math.sin(t * 6.28 + x * 0.7 + y * 0.5))
        pygame.draw.line(surface, (brilho, brilho, 255), (rect.x+3, rect.y+3), (rect.x+size-3, rect.y+size-3), 1)
        pygame.draw.line(surface, (brilho, brilho, 255), (rect.x+size-3, rect.y+3), (rect.x+3, rect.y+size-3), 1)
        pygame.draw.rect(surface, (120, 180, 220), rect, 1)


class CrystalTile(Tile):
    def __init__(self):
        super().__init__("Cristal Azul", "Water", (40, 80, 180), False, 0)

    def draw(self, surface, x, y, size, offset_x=0, offset_y=0):
        import math
        rect = pygame.Rect(x * size - offset_x, y * size - offset_y, size, size)
        pygame.draw.rect(surface, (20, 50, 120), rect)
        t = (pygame.time.get_ticks() % 1500) / 1500.0
        glow = int(80 + 120 * abs(math.sin(t * 3.14 + x + y)))
        cx, cy = rect.centerx, rect.centery
        pts = [(cx, rect.y+2), (rect.x+size-4, cy), (cx, rect.y+size-2), (rect.x+4, cy)]
        pygame.draw.polygon(surface, (glow, glow, 255), pts)
        pygame.draw.polygon(surface, (180, 220, 255), pts, 1)


class RiverTile(Tile):
    def __init__(self):
        super().__init__("Rio", "Water", (30, 100, 200), True, 3)

    def draw(self, surface, x, y, size, offset_x=0, offset_y=0):
        import math
        rect = pygame.Rect(x * size - offset_x, y * size - offset_y, size, size)
        pygame.draw.rect(surface, (20, 80, 180), rect)
        t = (pygame.time.get_ticks() % 1000) / 1000.0
        shift = int((t + x * 0.3) * size) % size
        for i in range(3):
            wy = rect.y + size // 4 * (i + 1)
            wx = rect.x + (shift + i * 5) % (size - 4)
            lighter = (60, 160, 255)
            pygame.draw.line(surface, lighter, (wx, wy), (wx + size // 3, wy), 2)
        pygame.draw.rect(surface, (0, 50, 140), rect, 1)


class WetSandTile(Tile):
    def __init__(self):
        super().__init__("Areia Úmida", "Water", (100, 120, 100), True, 0)

    def draw(self, surface, x, y, size, offset_x=0, offset_y=0):
        rect = pygame.Rect(x * size - offset_x, y * size - offset_y, size, size)
        pygame.draw.rect(surface, self.color, rect)
        for i in range(4):
            px2 = rect.x + (i * 7 + x * 3) % (size - 4)
            py2 = rect.y + (i * 5 + y * 3) % (size - 4)
            pygame.draw.circle(surface, (70, 100, 80), (px2, py2), 1)
        pygame.draw.rect(surface, (60, 90, 70), rect, 1)


# ---------------------------------------------------------------------------
# Tiles temáticos — Região Fogo (Leste)
# ---------------------------------------------------------------------------
class LavaTile(Tile):
    def __init__(self):
        super().__init__("Lava", "Fire", (200, 50, 0), True, 8)

    def on_step(self, player, map_manager=None):
        dmg = self.damage_on_step * (2 if getattr(player, "element", "") == "Grass" else 1)
        player.take_damage(dmg)

    def draw(self, surface, x, y, size, offset_x=0, offset_y=0):
        import math
        rect = pygame.Rect(x * size - offset_x, y * size - offset_y, size, size)
        pygame.draw.rect(surface, (180, 40, 0), rect)
        t = pygame.time.get_ticks() / 1000.0
        for i in range(3):
            bx = rect.x + size // 4 * (i + 1)
            phase = math.sin(t * 2.5 + i * 1.2 + x * 0.4 + y * 0.3)
            by = rect.centery + int(phase * size // 5)
            r = int(3 + 2 * abs(phase))
            pygame.draw.circle(surface, (255, 160 + int(60 * abs(phase)), 0), (bx, by), r)
        pygame.draw.rect(surface, (120, 20, 0), rect, 1)


class HotRockTile(Tile):
    tile_sprite_key = "hot_rock"

    def __init__(self):
        super().__init__("Rocha Vulcânica", "Fire", (50, 30, 20), True, 0)

    def draw(self, surface, x, y, size, offset_x=0, offset_y=0):
        import math
        rect = pygame.Rect(x * size - offset_x, y * size - offset_y, size, size)
        pygame.draw.rect(surface, self.color, rect)
        t = pygame.time.get_ticks() / 1000.0
        for i in range(3):
            cx2 = rect.x + (i * 9 + x * 5) % (size - 6) + 3
            cy2 = rect.y + (i * 7 + y * 4) % (size - 6) + 3
            glow = int(100 + 100 * abs(math.sin(t * 1.5 + i + x * 0.2)))
            pygame.draw.line(surface, (glow, glow // 3, 0),
                             (cx2, cy2), (cx2 + 4, cy2 + 2), 1)
        pygame.draw.rect(surface, (30, 15, 5), rect, 1)


class AshTile(Tile):
    tile_sprite_key = "ash"

    def __init__(self):
        super().__init__("Cinza", "Fire", (140, 130, 120), True, 0)

    def draw(self, surface, x, y, size, offset_x=0, offset_y=0):
        rect = pygame.Rect(x * size - offset_x, y * size - offset_y, size, size)
        pygame.draw.rect(surface, self.color, rect)
        for i in range(6):
            px2 = rect.x + (i * 5 + x * 3) % (size - 2)
            py2 = rect.y + (i * 4 + y * 5) % (size - 2)
            pygame.draw.circle(surface, (80, 70, 65), (px2, py2), 1)
        pygame.draw.rect(surface, (100, 90, 80), rect, 1)


class EmberTile(Tile):
    def __init__(self):
        super().__init__("Brasa", "Fire", (100, 40, 10), True, 2)

    def draw(self, surface, x, y, size, offset_x=0, offset_y=0):
        import math
        rect = pygame.Rect(x * size - offset_x, y * size - offset_y, size, size)
        pygame.draw.rect(surface, self.color, rect)
        t = pygame.time.get_ticks() / 1000.0
        for i in range(4):
            bx = rect.x + (i * 7 + x * 4) % (size - 4) + 2
            by = rect.y + (i * 5 + y * 3) % (size - 4) + 2
            pulse = abs(math.sin(t * 3.0 + i + x * 0.5))
            c = int(180 + 75 * pulse)
            pygame.draw.circle(surface, (c, c // 4, 0), (bx, by), 1)
        pygame.draw.rect(surface, (70, 20, 0), rect, 1)


# ---------------------------------------------------------------------------
# Tiles temáticos — Região Vento (Norte)
# ---------------------------------------------------------------------------
class CloudTile(Tile):
    def __init__(self):
        super().__init__("Nuvem", "Air", (210, 230, 250), True, 0)

    def draw(self, surface, x, y, size, offset_x=0, offset_y=0):
        import math
        rect = pygame.Rect(x * size - offset_x, y * size - offset_y, size, size)
        pygame.draw.rect(surface, (170, 200, 230), rect)
        t = pygame.time.get_ticks() / 1000.0
        shift = int(math.sin(t * 0.5 + x * 0.3) * 3)
        pygame.draw.ellipse(surface, (230, 240, 255),
            pygame.Rect(rect.x + 2 + shift, rect.y + size // 3, size - 4, size // 3))
        pygame.draw.ellipse(surface, (200, 220, 245),
            pygame.Rect(rect.x + 4 + shift, rect.y + size // 2, size - 8, size // 4))
        pygame.draw.rect(surface, (150, 180, 210), rect, 1)


class SkyPathTile(Tile):
    def __init__(self):
        super().__init__("Plataforma Celeste", "Air", (200, 215, 235), True, 0)

    def draw(self, surface, x, y, size, offset_x=0, offset_y=0):
        import math
        rect = pygame.Rect(x * size - offset_x, y * size - offset_y, size, size)
        pygame.draw.rect(surface, self.color, rect)
        t = pygame.time.get_ticks() / 1000.0
        glow = int(180 + 60 * abs(math.sin(t * 1.2 + x * 0.5)))
        pygame.draw.rect(surface, (glow, glow, 255), rect.inflate(-4, -4), 2)
        pygame.draw.rect(surface, (130, 160, 200), rect, 1)


class WindyGrassTile(Tile):
    def __init__(self):
        super().__init__("Grama Ventosa", "Air", (80, 170, 100), True, 0)

    def draw(self, surface, x, y, size, offset_x=0, offset_y=0):
        import math
        rect = pygame.Rect(x * size - offset_x, y * size - offset_y, size, size)
        pygame.draw.rect(surface, self.color, rect)
        t = pygame.time.get_ticks() / 1000.0
        for i in range(4):
            bx = rect.x + size // 5 * (i + 1)
            sway = int(math.sin(t * 3.0 + i * 0.8 + x * 0.4) * 3)
            pygame.draw.line(surface, (50, 140, 60),
                             (bx, rect.y + size - 4),
                             (bx + sway, rect.y + size // 2), 1)
        pygame.draw.rect(surface, (40, 110, 40), rect, 1)


class FeatherTile(Tile):
    def __init__(self):
        super().__init__("Penas", "Air", (230, 235, 245), True, 0)

    def draw(self, surface, x, y, size, offset_x=0, offset_y=0):
        import math
        rect = pygame.Rect(x * size - offset_x, y * size - offset_y, size, size)
        pygame.draw.rect(surface, (200, 210, 230), rect)
        t = pygame.time.get_ticks() / 1000.0
        for i in range(2):
            fx = rect.x + size // 3 * (i + 1)
            fy = rect.y + size // 4 + int(math.sin(t * 1.5 + i + x) * 2)
            pygame.draw.line(surface, (255, 255, 255), (fx, fy), (fx + 3, fy + 8), 2)
            pygame.draw.line(surface, (200, 210, 240), (fx, fy), (fx - 3, fy + 8), 1)
        pygame.draw.rect(surface, (160, 175, 200), rect, 1)


# ---------------------------------------------------------------------------
# Tiles temáticos — Região Elétrica (Sul)
# ---------------------------------------------------------------------------
class SandTile(Tile):
    tile_sprite_key = "sand"

    def __init__(self):
        super().__init__("Areia", "Electric", (210, 190, 100), True, 0)

    def draw(self, surface, x, y, size, offset_x=0, offset_y=0):
        rect = pygame.Rect(x * size - offset_x, y * size - offset_y, size, size)
        pygame.draw.rect(surface, self.color, rect)
        for i in range(5):
            px2 = rect.x + (i * 6 + x * 4) % (size - 2)
            py2 = rect.y + (i * 5 + y * 3) % (size - 2)
            pygame.draw.circle(surface, (180, 160, 70), (px2, py2), 1)
        pygame.draw.rect(surface, (170, 150, 60), rect, 1)


class ChargedSandTile(Tile):
    def __init__(self):
        super().__init__("Areia Carregada", "Electric", (190, 175, 60), True, 0)

    def draw(self, surface, x, y, size, offset_x=0, offset_y=0):
        import math
        rect = pygame.Rect(x * size - offset_x, y * size - offset_y, size, size)
        pygame.draw.rect(surface, (190, 175, 60), rect)
        t = pygame.time.get_ticks() / 1000.0
        for i in range(2):
            if math.sin(t * 8.0 + i * 1.5 + x * 0.7 + y * 0.4) > 0.6:
                lx = rect.x + (i * 11 + x * 3) % (size - 8) + 4
                ly = rect.y + (i * 8 + y * 5) % (size - 8) + 4
                pygame.draw.line(surface, (255, 255, 80),
                                 (lx, ly), (lx + 4, ly - 4), 1)
                pygame.draw.line(surface, (255, 255, 80),
                                 (lx + 4, ly - 4), (lx + 2, ly - 8), 1)
        pygame.draw.rect(surface, (150, 135, 30), rect, 1)


class MetalTile(Tile):
    def __init__(self):
        super().__init__("Metal", "Electric", (150, 155, 170), True, 0)

    def draw(self, surface, x, y, size, offset_x=0, offset_y=0):
        rect = pygame.Rect(x * size - offset_x, y * size - offset_y, size, size)
        pygame.draw.rect(surface, self.color, rect)
        refl = (200, 205, 220)
        pygame.draw.line(surface, refl, (rect.x, rect.y), (rect.x+size, rect.y), 1)
        pygame.draw.line(surface, refl, (rect.x, rect.y), (rect.x, rect.y+size), 1)
        pygame.draw.rect(surface, (100, 105, 120), rect, 1)


class LightningCrystalTile(Tile):
    def __init__(self):
        super().__init__("Cristal Raio", "Electric", (220, 200, 20), False, 0)

    def draw(self, surface, x, y, size, offset_x=0, offset_y=0):
        import math
        rect = pygame.Rect(x * size - offset_x, y * size - offset_y, size, size)
        pygame.draw.rect(surface, (100, 90, 10), rect)
        t = pygame.time.get_ticks() / 1000.0
        glow = int(150 + 105 * abs(math.sin(t * 4.0 + x + y)))
        cx2, cy2 = rect.centerx, rect.centery
        pts = [(cx2, rect.y+2), (rect.x+size-3, cy2), (cx2, rect.y+size-2), (rect.x+3, cy2)]
        pygame.draw.polygon(surface, (glow, glow, 0), pts)
        pygame.draw.polygon(surface, (255, 255, 180), pts, 1)


# ---------------------------------------------------------------------------
# Tiles temáticos — Região Centro
# ---------------------------------------------------------------------------
class FlowerGrassTile(Tile):
    tile_sprite_key = "flower_grass"

    def __init__(self):
        super().__init__("Grama Florida", "Grass", (60, 150, 60), True, 0)

    def draw(self, surface, x, y, size, offset_x=0, offset_y=0):
        if self._try_draw_sprite(surface, x, y, size, offset_x, offset_y):
            return
        rect = pygame.Rect(x * size - int(offset_x), y * size - int(offset_y), size, size)
        pygame.draw.rect(surface, self.color, rect)
        stripe = (40, 120, 40)
        for i in range(3):
            sx2 = rect.x + size // 4 * (i + 1)
            pygame.draw.line(surface, stripe, (sx2, rect.y+4), (sx2, rect.y+size-4), 1)
        colors = [(255, 80, 80), (255, 220, 50), (150, 100, 255)]
        for i in range(2):
            fx = rect.x + (i * 11 + x * 7) % (size - 6) + 3
            fy = rect.y + (i * 8 + y * 5) % (size - 6) + 3
            pygame.draw.circle(surface, colors[(x + y + i) % 3], (fx, fy), 2)
        pygame.draw.rect(surface, (30, 100, 30), rect, 1)


class BushTile(Tile):
    tile_sprite_key = "bush"

    def __init__(self):
        super().__init__("Arbusto", "Grass", (30, 100, 30), False, 0)

    def draw(self, surface, x, y, size, offset_x=0, offset_y=0):
        if self._try_draw_sprite(surface, x, y, size, offset_x, offset_y):
            return
        rect = pygame.Rect(x * size - int(offset_x), y * size - int(offset_y), size, size)
        pygame.draw.rect(surface, (40, 80, 20), rect)
        for ox, oy, r in [(-4, 0, 7), (4, -2, 6), (0, 4, 6), (-3, -3, 5)]:
            cx2 = rect.centerx + ox
            cy2 = rect.centery + oy
            if rect.collidepoint(cx2, cy2):
                pygame.draw.circle(surface, (50, 140, 30), (cx2, cy2), r)
        pygame.draw.rect(surface, (20, 60, 10), rect, 1)


class TreeTile(Tile):
    tile_sprite_key = "tree"

    def __init__(self):
        super().__init__("Árvore", "Grass", (30, 80, 20), False, 0)

    def draw(self, surface, x, y, size, offset_x=0, offset_y=0):
        if self._try_draw_sprite(surface, x, y, size, offset_x, offset_y):
            return
        rect = pygame.Rect(x * size - int(offset_x), y * size - int(offset_y), size, size)
        pygame.draw.rect(surface, (20, 60, 10), rect)
        trunk_r = pygame.Rect(rect.centerx - 3, rect.centery, 6, size // 2)
        pygame.draw.rect(surface, (100, 60, 20), trunk_r)
        pygame.draw.circle(surface, (40, 140, 30), (rect.centerx, rect.centery - 2), size // 3)
        pygame.draw.circle(surface, (60, 170, 40), (rect.centerx - 3, rect.centery - 4), size // 5)
        pygame.draw.circle(surface, (35, 120, 25), (rect.centerx + 3, rect.centery - 3), size // 5)
        pygame.draw.rect(surface, (10, 40, 5), rect, 1)


class WoodPathTile(Tile):
    tile_sprite_key = "wood_path"

    def __init__(self):
        super().__init__("Caminho de Madeira", "None", (160, 100, 50), True, 0)

    def draw(self, surface, x, y, size, offset_x=0, offset_y=0):
        rect = pygame.Rect(x * size - offset_x, y * size - offset_y, size, size)
        pygame.draw.rect(surface, self.color, rect)
        grain = (140, 85, 40)
        for i in range(3):
            gy = rect.y + size // 4 * (i + 1)
            pygame.draw.line(surface, grain, (rect.x+2, gy), (rect.x+size-2, gy), 1)
        pygame.draw.rect(surface, (110, 65, 25), rect, 1)


# ---------------------------------------------------------------------------
# Tiles de caminho conectivo
# ---------------------------------------------------------------------------
class StoneRoadTile(Tile):
    tile_sprite_key = "stone_road"

    def __init__(self):
        super().__init__("Estrada de Pedra", "None", (180, 175, 165), True, 0)

    def draw(self, surface, x, y, size, offset_x=0, offset_y=0):
        rect = pygame.Rect(x * size - offset_x, y * size - offset_y, size, size)
        pygame.draw.rect(surface, self.color, rect)
        for i in range(2):
            sx2 = rect.x + size // 3 * (i + 1)
            pygame.draw.line(surface, (140, 135, 125), (sx2, rect.y+2), (sx2, rect.y+size-2), 1)
        pygame.draw.rect(surface, (130, 125, 115), rect, 1)


class WoodBridgeTile(Tile):
    tile_sprite_key = "wood_bridge"

    def __init__(self):
        super().__init__("Ponte de Madeira", "None", (140, 90, 45), True, 0)

    def draw(self, surface, x, y, size, offset_x=0, offset_y=0):
        rect = pygame.Rect(x * size - offset_x, y * size - offset_y, size, size)
        pygame.draw.rect(surface, (20, 80, 180), rect)
        plank_color = (140, 90, 45)
        for i in range(4):
            py2 = rect.y + size // 4 * i + 2
            plank_r = pygame.Rect(rect.x + 2, py2, size - 4, size // 4 - 2)
            pygame.draw.rect(surface, plank_color, plank_r)
            pygame.draw.rect(surface, (100, 60, 25), plank_r, 1)


# ---------------------------------------------------------------------------
# Tiles de arena (salas de batalha)
# ---------------------------------------------------------------------------
class IceArenaTile(Tile):
    def __init__(self):
        super().__init__("Arena de Gelo", "Water", (160, 210, 240), True, 0)

    def draw(self, surface, x, y, size, offset_x=0, offset_y=0):
        import math
        rect = pygame.Rect(x * size - offset_x, y * size - offset_y, size, size)
        pygame.draw.rect(surface, self.color, rect)
        t = pygame.time.get_ticks() / 1000.0
        alpha = int(30 + 20 * math.sin(t * 1.5 + x * 0.6 + y * 0.4))
        pygame.draw.rect(surface, (200, 240, 255), rect.inflate(-alpha // 3, -alpha // 3), 1)
        pygame.draw.rect(surface, (100, 170, 210), rect, 1)


class VolcanoFloorTile(Tile):
    def __init__(self):
        super().__init__("Chão Vulcânico", "Fire", (40, 25, 15), True, 0)

    def draw(self, surface, x, y, size, offset_x=0, offset_y=0):
        import math
        rect = pygame.Rect(x * size - offset_x, y * size - offset_y, size, size)
        pygame.draw.rect(surface, self.color, rect)
        t = pygame.time.get_ticks() / 1000.0
        for i in range(3):
            cx2 = rect.x + (i * 8 + x * 5) % (size - 4) + 2
            cy2 = rect.y + (i * 6 + y * 4) % (size - 4) + 2
            glow = int(80 + 80 * abs(math.sin(t * 2.0 + i + x * 0.3)))
            pygame.draw.line(surface, (glow, glow // 3, 0), (cx2, cy2), (cx2 + 5, cy2 + 3), 1)
        pygame.draw.rect(surface, (20, 10, 5), rect, 1)


class SkyArenaTile(Tile):
    def __init__(self):
        super().__init__("Arena Celeste", "Air", (195, 215, 240), True, 0)

    def draw(self, surface, x, y, size, offset_x=0, offset_y=0):
        import math
        rect = pygame.Rect(x * size - offset_x, y * size - offset_y, size, size)
        pygame.draw.rect(surface, self.color, rect)
        t = pygame.time.get_ticks() / 1000.0
        glow = int(200 + 55 * abs(math.sin(t * 0.8 + x * 0.4)))
        pygame.draw.rect(surface, (glow, glow, 255), rect.inflate(-6, -6), 2)
        pygame.draw.rect(surface, (140, 170, 210), rect, 1)


class MetalArenaTile(Tile):
    def __init__(self):
        super().__init__("Arena Metálica", "Electric", (120, 130, 150), True, 0)

    def draw(self, surface, x, y, size, offset_x=0, offset_y=0):
        import math
        rect = pygame.Rect(x * size - offset_x, y * size - offset_y, size, size)
        pygame.draw.rect(surface, self.color, rect)
        t = pygame.time.get_ticks() / 1000.0
        glow = int(50 + 50 * abs(math.sin(t * 2.0 + x * 0.5 + y * 0.3)))
        pygame.draw.rect(surface, (80, 100, 130 + glow // 3), rect.inflate(-4, -4), 1)
        cx2, cy2 = rect.centerx, rect.centery
        hs = size // 4
        pts = [(cx2, cy2 - hs), (cx2 + hs, cy2), (cx2, cy2 + hs), (cx2 - hs, cy2)]
        pygame.draw.polygon(surface, (150, 160, 180), pts, 1)
        pygame.draw.rect(surface, (80, 90, 110), rect, 1)


class DeepWaterTile(Tile):
    def __init__(self):
        super().__init__("Água Profunda", "Water", (10, 40, 130), False, 0)

    def draw(self, surface, x, y, size, offset_x=0, offset_y=0):
        import math
        rect = pygame.Rect(x * size - offset_x, y * size - offset_y, size, size)
        pygame.draw.rect(surface, self.color, rect)
        t = pygame.time.get_ticks() / 1000.0
        for i in range(2):
            wy = rect.y + size // 3 * (i + 1)
            shift = int(math.sin(t * 1.5 + i + x * 0.5) * 4)
            pygame.draw.line(surface, (30, 80, 180),
                             (rect.x + 2 + shift, wy),
                             (rect.x + size - 2 + shift, wy), 1)
        pygame.draw.rect(surface, (5, 20, 80), rect, 1)


class SkyVoidTile(Tile):
    def __init__(self):
        super().__init__("Vazio Celeste", "Air", (100, 140, 200), False, 0)

    def draw(self, surface, x, y, size, offset_x=0, offset_y=0):
        import math
        rect = pygame.Rect(x * size - offset_x, y * size - offset_y, size, size)
        pygame.draw.rect(surface, self.color, rect)
        t = pygame.time.get_ticks() / 1000.0
        for i in range(3):
            cx2 = rect.x + (i * 9 + x * 4) % (size - 4) + 2
            cy2 = rect.y + (i * 7 + y * 3) % (size - 4) + 2
            r = int(2 + 2 * abs(math.sin(t * 0.7 + i + x)))
            pygame.draw.circle(surface, (200, 220, 250), (cx2, cy2), r)
        pygame.draw.rect(surface, (70, 110, 170), rect, 1)


# ---------------------------------------------------------------------------
# Tiles decorativos — Salas de batalha
# ---------------------------------------------------------------------------
class IceStalactiteTile(Tile):
    def __init__(self):
        super().__init__("Estalactite de Gelo", "Water", (140, 200, 230), False, 0)

    def draw(self, surface, x, y, size, offset_x=0, offset_y=0):
        import math
        rect = pygame.Rect(x * size - offset_x, y * size - offset_y, size, size)
        pygame.draw.rect(surface, (100, 160, 200), rect)
        t = pygame.time.get_ticks() / 1000.0
        for i in range(3):
            tip_x  = rect.x + size // 4 * (i + 1)
            height = size // 2 + int(4 * abs(math.sin(t * 0.5 + i + x)))
            pts    = [(tip_x - 4, rect.y + 2), (tip_x + 4, rect.y + 2),
                      (tip_x, rect.y + height)]
            pygame.draw.polygon(surface, (190, 230, 255), pts)
            pygame.draw.polygon(surface, (140, 200, 240), pts, 1)
        pygame.draw.rect(surface, (80, 140, 190), rect, 1)


class BubbleTile(Tile):
    def __init__(self):
        super().__init__("Bolhas", "Water", (20, 80, 180), True, 0)

    def draw(self, surface, x, y, size, offset_x=0, offset_y=0):
        import math
        rect = pygame.Rect(x * size - offset_x, y * size - offset_y, size, size)
        pygame.draw.rect(surface, (15, 60, 150), rect)
        t = pygame.time.get_ticks() / 1000.0
        for i in range(3):
            phase  = (t * 0.8 + i * 0.7 + x * 0.3) % 1.0
            bx2    = rect.x + (i * 9 + x * 5) % (size - 6) + 3
            by2    = rect.y + size - int(phase * size)
            r      = int(2 + 2 * abs(math.sin(t * 1.2 + i)))
            alpha2 = int(180 * (1 - phase))
            s      = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (100, 180, 255, alpha2), (r, r), r)
            pygame.draw.circle(s, (200, 240, 255, alpha2 // 2), (r, r), r, 1)
            surface.blit(s, (bx2 - r, by2 - r))
        pygame.draw.rect(surface, (10, 40, 120), rect, 1)


class LavaDropTile(Tile):
    def __init__(self):
        super().__init__("Pingo de Lava", "Fire", (80, 20, 5), True, 2)

    def draw(self, surface, x, y, size, offset_x=0, offset_y=0):
        import math
        rect = pygame.Rect(x * size - offset_x, y * size - offset_y, size, size)
        pygame.draw.rect(surface, (55, 15, 3), rect)
        t = pygame.time.get_ticks() / 1000.0
        for i in range(2):
            phase  = (t * 1.2 + i * 0.6 + y * 0.4) % 1.0
            dx2    = (i * 11 + x * 7) % (size - 8) + 4
            dy2    = int(phase * (size - 4))
            cv     = int(200 + 55 * abs(math.sin(t * 3 + i)))
            s      = pygame.Surface((6, 8), pygame.SRCALPHA)
            pts    = [(3, 0), (6, 5), (3, 8), (0, 5)]
            pygame.draw.polygon(s, (cv, cv // 3, 0, 200), pts)
            surface.blit(s, (rect.x + dx2 - 3, rect.y + dy2 - 4))
        pygame.draw.rect(surface, (40, 8, 0), rect, 1)


class CircuitFloorTile(Tile):
    def __init__(self):
        super().__init__("Chão de Circuito", "Electric", (30, 38, 50), True, 0)

    def draw(self, surface, x, y, size, offset_x=0, offset_y=0):
        import math
        rect = pygame.Rect(x * size - offset_x, y * size - offset_y, size, size)
        pygame.draw.rect(surface, self.color, rect)
        t = pygame.time.get_ticks() / 1000.0
        # Linhas de circuito estáticas
        cx2, cy2 = rect.x + size // 2, rect.y + size // 2
        pygame.draw.line(surface, (0, 80, 60), (rect.x, cy2), (rect.right, cy2), 1)
        pygame.draw.line(surface, (0, 80, 60), (cx2, rect.y), (cx2, rect.bottom), 1)
        # Nó central pulsante
        pulse = abs(math.sin(t * 2.5 + x * 0.4 + y * 0.3))
        cv    = int(60 + 140 * pulse)
        pygame.draw.circle(surface, (0, cv, cv // 2), (cx2, cy2), 3)
        # Pulsos viajando pelas linhas
        prog = (t * 1.8 + x * 0.25 + y * 0.2) % 1.0
        px2  = rect.x + int(prog * size)
        pygame.draw.circle(surface, (0, 200, 120), (px2, cy2), 2)
        pygame.draw.rect(surface, (20, 55, 40), rect, 1)


class NeonBorderTile(Tile):
    def __init__(self):
        super().__init__("Tubo Neon", "Electric", (20, 20, 30), False, 0)

    def draw(self, surface, x, y, size, offset_x=0, offset_y=0):
        import math
        rect = pygame.Rect(x * size - offset_x, y * size - offset_y, size, size)
        pygame.draw.rect(surface, (15, 15, 25), rect)
        t   = pygame.time.get_ticks() / 1000.0
        gv  = int(100 + 155 * abs(math.sin(t * 2.0 + x * 0.5 + y * 0.4)))
        pygame.draw.rect(surface, (0, gv, gv // 3),
                         rect.inflate(-6, -6), 2, border_radius=3)
        pygame.draw.rect(surface, (10, 10, 20), rect, 1)


# ---------------------------------------------------------------------------
# Tiles temáticos — Região Sombra
# ---------------------------------------------------------------------------
class VoidFloorTile(Tile):
    def __init__(self):
        super().__init__("Chão do Vazio", "Dark", (15, 8, 28), True, 0)

    def draw(self, surface, x, y, size, offset_x=0, offset_y=0):
        import math
        rect = pygame.Rect(x * size - offset_x, y * size - offset_y, size, size)
        pygame.draw.rect(surface, self.color, rect)
        t = pygame.time.get_ticks() / 1000.0
        for i in range(3):
            px2 = rect.x + (i * 9 + x * 5) % (size - 4) + 2
            py2 = rect.y + (i * 7 + y * 3) % (size - 4) + 2
            pulse = abs(math.sin(t * 2.5 + i + x * 0.4 + y * 0.3))
            r = int(1 + 2 * pulse)
            cv = int(80 + 120 * pulse)
            pygame.draw.circle(surface, (cv // 2, 0, cv), (px2, py2), r)
        pygame.draw.rect(surface, (30, 5, 50), rect, 1)


class ShadowCrystalTile(Tile):
    def __init__(self):
        super().__init__("Cristal das Sombras", "Dark", (60, 10, 100), False, 0)

    def draw(self, surface, x, y, size, offset_x=0, offset_y=0):
        import math
        rect = pygame.Rect(x * size - offset_x, y * size - offset_y, size, size)
        pygame.draw.rect(surface, (10, 3, 20), rect)
        t = pygame.time.get_ticks() / 1000.0
        glow = int(80 + 120 * abs(math.sin(t * 1.8 + x + y)))
        cx2, cy2 = rect.centerx, rect.centery
        pts = [(cx2, rect.y + 2), (rect.x + size - 4, cy2 - 2),
               (cx2, rect.y + size - 2), (rect.x + 4, cy2 + 2)]
        pygame.draw.polygon(surface, (glow // 2, 0, glow), pts)
        pygame.draw.polygon(surface, (180, 100, 255), pts, 1)


class DarkMistTile(Tile):
    def __init__(self):
        super().__init__("Névoa Sombria", "Dark", (25, 10, 40), True, 0)

    def draw(self, surface, x, y, size, offset_x=0, offset_y=0):
        import math
        rect = pygame.Rect(x * size - offset_x, y * size - offset_y, size, size)
        pygame.draw.rect(surface, self.color, rect)
        t = pygame.time.get_ticks() / 1000.0
        alpha_factor = abs(math.sin(t * 1.2 + x * 0.5 + y * 0.4))
        mc = int(60 + 80 * alpha_factor)
        pygame.draw.ellipse(surface, (mc // 3, 0, mc),
            pygame.Rect(rect.x + 3, rect.y + size // 3, size - 6, size // 3))
        pygame.draw.rect(surface, (15, 5, 25), rect, 1)


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
        import math
        rect = pygame.Rect(x * size - int(offset_x), y * size - int(offset_y), size, size)
        dark = tuple(max(c - 60, 0) for c in self.color)
        pygame.draw.rect(surface, dark, rect)

        t  = pygame.time.get_ticks() / 1000.0
        cx, cy = rect.centerx, rect.centery

        # Anéis pulsantes concêntricos
        for ring in range(3, 0, -1):
            phase = math.sin(t * 2.5 + ring * 0.9)
            r = size // 2 - ring * 3 + int(phase * 2)
            if r > 1:
                brightness = 60 + ring * 35
                c_rgb = tuple(min(c + brightness, 255) for c in self.color)
                thick = 2 if ring == 3 else 1
                pygame.draw.circle(surface, c_rgb, (cx, cy), r, thick)

        # 4 partículas rotacionando
        for i in range(4):
            angle = t * 2.5 + i * (math.pi / 2)
            pr = size // 3
            ppx = cx + int(math.cos(angle) * pr)
            ppy = cy + int(math.sin(angle) * pr)
            bright = tuple(min(c + 130, 255) for c in self.color)
            pygame.draw.circle(surface, bright, (ppx, ppy), 2)

        # Anel externo pulsante
        outer_r = size // 2 - 1 + int(abs(math.sin(t * 2.0)) * 3)
        outer_c = tuple(min(c + 50, 255) for c in self.color)
        pygame.draw.circle(surface, outer_c, (cx, cy), outer_r, 1)
        pygame.draw.rect(surface, (210, 210, 210), rect, 1)


# ---------------------------------------------------------------------------
# Map (Stage baseado em tiles) — com suporte a imagem de fundo
# ---------------------------------------------------------------------------
class Map(Stage):
    def __init__(self, name, tile_matrix, tile_types,
                 tile_size=TILE_SIZE, bg_image: pygame.Surface | None = None,
                 world_image_file: str | None = None):
        super().__init__(name)
        self.matrix      = tile_matrix
        self.tile_types  = tile_types
        self.tile_size   = tile_size
        self.width       = len(tile_matrix[0]) if tile_matrix else 0
        self.height      = len(tile_matrix)
        self.camera_offset_x = 0.0
        self.camera_offset_y = 0.0
        self.bg_image    = bg_image   # pygame.Surface opcional
        # Nome do PNG usado como mundo rolante (mapa/arena). Quando definido,
        # a imagem cobre o mundo e só os portais são desenhados por cima.
        self.world_image_file = world_image_file

    def get_tile_at(self, grid_x, grid_y):
        if 0 <= grid_y < self.height and 0 <= grid_x < self.width:
            return self.tile_types.get(self.matrix[grid_y][grid_x])
        return None

    def is_walkable(self, grid_x, grid_y):
        tile = self.get_tile_at(grid_x, grid_y)
        return tile.is_walkable if tile else False

    def update_camera(self, player_pixel_x, player_pixel_y, dt=0.016):
        target_x = float(player_pixel_x - SCREEN_WIDTH  // 2)
        target_y = float(player_pixel_y - SCREEN_HEIGHT // 2)
        max_x = max(0.0, self.width  * self.tile_size - SCREEN_WIDTH)
        max_y = max(0.0, self.height * self.tile_size - SCREEN_HEIGHT)
        target_x = max(0.0, min(target_x, max_x))
        target_y = max(0.0, min(target_y, max_y))
        alpha = min(1.0, 8.0 * dt)
        self.camera_offset_x += (target_x - self.camera_offset_x) * alpha
        self.camera_offset_y += (target_y - self.camera_offset_y) * alpha

    def draw(self, surface: pygame.Surface):
        ts  = self.tile_size
        ox  = int(self.camera_offset_x)
        oy  = int(self.camera_offset_y)
        x0  = max(0, ox // ts)
        y0  = max(0, oy // ts)
        x1  = min(self.width,  x0 + SCREEN_WIDTH  // ts + 2)
        y1  = min(self.height, y0 + SCREEN_HEIGHT // ts + 2)

        # Modo imagem-mundo: PNG cobre o mundo, só portais desenham por cima
        if self.world_image_file:
            world_w = self.width  * ts
            world_h = self.height * ts
            img = get_scene_image(self.world_image_file, world_w, world_h)
            if img:
                surface.blit(img, (-ox, -oy))
            else:
                surface.fill((20, 20, 30))
            for y in range(y0, y1):
                for x in range(x0, x1):
                    tile = self.get_tile_at(x, y)
                    if isinstance(tile, PortalTile):
                        tile.draw(surface, x, y, ts,
                                  self.camera_offset_x, self.camera_offset_y)
            return

        if self.bg_image:
            scaled = pygame.transform.scale(self.bg_image, (SCREEN_WIDTH, SCREEN_HEIGHT))
            surface.blit(scaled, (0, 0))
        else:
            surface.fill((20, 20, 30))

        for y in range(y0, y1):
            for x in range(x0, x1):
                tile = self.get_tile_at(x, y)
                if tile:
                    tile.draw(surface, x, y, ts,
                              self.camera_offset_x, self.camera_offset_y)


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
                world_image_file=data.get("world_image"),
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