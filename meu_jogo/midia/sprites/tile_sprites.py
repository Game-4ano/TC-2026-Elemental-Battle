"""
meu_jogo/midia/sprites/tile_sprites.py

Sprites de pixel art 16×16 para tiles do mapa.
Escalonados 2× no carregamento → 32×32 (= TILE_SIZE).

USO:
    from meu_jogo.midia.sprites.tile_sprites import get_tile_sprite, get_tile_frame_count
    sprite = get_tile_sprite("grass")
    sprite = get_tile_sprite("water", frame=1)
"""

import pygame

_SCALE = 2   # 16×16 → 32×32


def _build(pixels: list[str], palette: dict) -> pygame.Surface:
    h = len(pixels)
    w = max(len(r) for r in pixels)
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 0))
    for y, row in enumerate(pixels):
        for x, ch in enumerate(row):
            if ch == '.':
                continue
            color = palette.get(ch)
            if color:
                surf.set_at((x, y), color)
    return pygame.transform.scale(surf, (w * _SCALE, h * _SCALE))


# ─────────────────────────────────────────────────────────────────────
#  GRAMA
# ─────────────────────────────────────────────────────────────────────
_GRASS_P = {
    'G': (55, 145, 55), 'g': (38, 115, 38),
    'l': (78, 172, 60), 'L': (95, 195, 75),
}
_GRASS = [
    "GgGGgGGGgGGGgGGg",
    "GGGlGGGGGlGGGGlG",
    "gGGGGgGGGGgGGGGG",
    "GGGGGGgGGGGGgGGG",
    "GlGGGGGGlGGGGGlG",
    "GGGgGGGGGGgGGGGG",
    "GGGGGGGgGGGGGgGG",
    "gGGGlGGGGlGGGGGg",
    "GGGGGGGGGGGGGGGG",
    "GGlGGGGGGGlGGGGG",
    "GgGGGgGGGGGGgGGg",
    "GGGGGGGlGGGGGGGG",
    "GGGGGGGGGgGGGGGl",
    "gGGGlGGGGGGgGGGG",
    "GGGGGGGgGGGGGGGG",
    "GlGGGGGGGGlGGGGg",
]

# ─────────────────────────────────────────────────────────────────────
#  ÁGUA (2 frames — onda desloca)
# ─────────────────────────────────────────────────────────────────────
_WATER_P = {
    'B': (20, 85, 180), 'b': (35, 105, 200),
    'W': (75, 155, 235), 'w': (115, 185, 255),
}
_WATER_F0 = [
    "BbbBBbBBbBBbBBbB",
    "bBBBbBBBbBBBbBBB",
    "bbWwWbbBbWwWbBBb",
    "bBWwwWBbBWwwWBBb",
    "bBbWwWBBbBWwWBBb",
    "BBBbBBBBBbBBBBBB",
    "bBBBbBBBbBBBbBBB",
    "BbbBBbBBbBBbBBbB",
    "BbBBWwWbbBBWwWbB",
    "bBBBWwwWBbBBWwwW",
    "BBBBbWwWBBBBbWwW",
    "bBBBbBBBbBBBbBBB",
    "BbbBBbBBbBBbBBbB",
    "bBBBbBBBbBBBbBBB",
    "bbWwWbbBbWwWbBBb",
    "bBBBbBBBbBBBbBBB",
]
_WATER_F1 = [
    "bBBBbBBBbBBBbBBB",
    "BbbBBbBBbBBbBBbB",
    "BBBbBBBBBbBBBBBB",
    "bbWwWbbBbWwWbBBb",
    "bBWwwWBbBWwwWBBb",
    "bBbWwWBBbBWwWBBb",
    "bBBBbBBBbBBBbBBB",
    "BbbBBbBBbBBbBBbB",
    "bBBBbBBBbBBBbBBB",
    "BbBBWwWbbBBWwWbB",
    "bBBBWwwWBbBBWwwW",
    "BBBBbWwWBBBBbWwW",
    "bBBBbBBBbBBBbBBB",
    "BbbBBbBBbBBbBBbB",
    "bBBBbBBBbBBBbBBB",
    "BBBbBBBBBbBBBBBB",
]

# ─────────────────────────────────────────────────────────────────────
#  ROCHA / PAREDE
# ─────────────────────────────────────────────────────────────────────
_ROCK_P = {
    'D': (70, 52, 34), 'd': (90, 68, 45),
    'L': (112, 86, 58), 'l': (135, 108, 76),
    'K': (40, 28, 14), 'k': (55, 40, 22),
}
_ROCK = [
    "llllLlllLlllLLLL",
    "lLLLlLLLlLLLlLLL",
    "dLLdkLLdkLLdkLLd",
    "KddDKdddKdddKddd",
    "KDDDkDDDkDDDkDDD",
    "KDDDKDDDKDDDKDDd",
    "llllLlllLlllLLLL",
    "lLLLlLLLlLLLlLLL",
    "dLLdkLLdkLLdkLLd",
    "KddDKdddKdddKddd",
    "KDDDkDDDkDDDkDDD",
    "KDDDKDDDKDDDKDDd",
    "llllLlllLlllLLLL",
    "lLLLlLLLlLLLlLLL",
    "dLLdkLLdkLLdkLLd",
    "KDDDKDDDKDDDKddd",
]

# ─────────────────────────────────────────────────────────────────────
#  GRAMA FLORIDA (flores coloridas)
# ─────────────────────────────────────────────────────────────────────
_FLOWER_P = {
    'G': (55, 145, 55), 'g': (38, 115, 38),
    'l': (78, 172, 60),
    'R': (230, 70, 70),  'r': (255, 120, 120),
    'Y': (240, 210, 40), 'y': (255, 240, 100),
    'V': (160, 80, 220), 'v': (200, 140, 255),
    'W': (255, 255, 255),
}
_FLOWER = [
    "GGGRrRGGGGYyYGGG",
    "GGRrRrRGGYyYyYGG",
    "GGGRrRGGGGYyYGGG",
    "gGGGGGGgGGGGGGGg",
    "GGGGGgGGGGGGgGGG",
    "GGlGGGGGlGGGGGlG",
    "GGGGVvVGGGGRrRGG",
    "GGGVvVvVGGRrRrRG",
    "GGGGVvVGGGGRrRGG",
    "gGGGGGGgGGGGGGGg",
    "GGGGGgGGGGGGgGGG",
    "GGlGGGGGlGGGGGlG",
    "GGGYyYGGGGVvVGGG",
    "GGYyYyYGGVvVvVGG",
    "GGGYyYGGGGVvVGGG",
    "gGGGGGGgGGGGGGGg",
]

# ─────────────────────────────────────────────────────────────────────
#  ARBUSTO
# ─────────────────────────────────────────────────────────────────────
_BUSH_P = {
    'G': (35, 105, 30), 'g': (50, 140, 40),
    'l': (70, 170, 55), 'L': (90, 195, 70),
    'd': (20, 68, 15), 'D': (15, 50, 10),
    'T': (80, 55, 25),  # terra/tronco
}
_BUSH = [
    "DDDDDDdDDDDdDDDD",
    "DDdDdDDDdDDDDdDD",
    "dDgGGGggGGGGGgdD",
    "DdgGlLLlLlLlGgdD",
    "DdGGlLLLLLllGGdD",
    "DdGGLLLlLLLLGGdD",
    "DdGGgLlLLlgGGGdD",
    "DdGGGGgGggGGGGdD",
    "DdGGGGGGGGGGGGdD",
    "DDdGGGGgGGGGGddD",
    "DDDdGGGGGGGGddDD",
    "DDDDdGGGGGGdDDDD",
    "DDDDDddGGddDDDDD",
    "DDDDDDTTTTDDDDDD",
    "DDDDDDTTTTDDDDDD",
    "DDDDDDDDDDDDDDDD",
]

# ─────────────────────────────────────────────────────────────────────
#  ÁRVORE
# ─────────────────────────────────────────────────────────────────────
_TREE_P = {
    'G': (35, 115, 30), 'g': (50, 148, 42),
    'l': (70, 175, 55), 'L': (90, 200, 68),
    'd': (20, 72, 16), 'D': (12, 48, 8),
    'T': (90, 58, 22), 't': (115, 75, 30),
    'k': (50, 35, 12),
}
_TREE = [
    "DDDDDDdlLldDDDDD",
    "DDDDDdlLLLldDDDD",
    "DDDDdlLlLlLldDDD",
    "DDDdlLLLLLLLldDD",
    "DDdGGlLlLlLGGgdD",
    "DDdGGlLLLLlGGGdD",
    "DDdGGGlLlLGGGGdD",
    "DDDdGGGGGGGGgdDD",
    "DDDDdGGGGGGddDDD",
    "DDDDDddGGddDDDDD",
    "DDDDDDkTtTkDDDDD",
    "DDDDDDkTtTkDDDDD",
    "DDDDDDkTtTkDDDDD",
    "DDDDDDkTtTkDDDDD",
    "DDDdDDkTtTkDDdDD",
    "DDDdDDdddddDDdDD",
]

# ─────────────────────────────────────────────────────────────────────
#  CAMINHO DE MADEIRA
# ─────────────────────────────────────────────────────────────────────
_WOOD_P = {
    'W': (160, 100, 48), 'w': (140, 84, 38),
    'D': (105, 65, 25),  'd': (120, 78, 32),
    'K': (80,  48, 15),  'k': (70,  40, 10),
    'L': (180, 118, 58),
}
_WOOD_PATH = [
    "KkKkKkKkKkKkKkKk",
    "kWWWwWWWwWWWwWWW",
    "kWLWwWLWwWLWwWLW",
    "kWWWwWWWwWWWwWWW",
    "KDdDKDdDKDdDKDdD",
    "kWWWwWWWwWWWwWWW",
    "kWLWwWLWwWLWwWLW",
    "kWWWwWWWwWWWwWWW",
    "KkKkKkKkKkKkKkKk",
    "kWWWwWWWwWWWwWWW",
    "kWLWwWLWwWLWwWLW",
    "kWWWwWWWwWWWwWWW",
    "KDdDKDdDKDdDKDdD",
    "kWWWwWWWwWWWwWWW",
    "kWLWwWLWwWLWwWLW",
    "KkKkKkKkKkKkKkKk",
]

# ─────────────────────────────────────────────────────────────────────
#  ESTRADA DE PEDRA
# ─────────────────────────────────────────────────────────────────────
_STONE_ROAD_P = {
    'L': (185, 180, 168), 'M': (158, 152, 140),
    'D': (128, 123, 112), 'K': (95,  90,  80),
    'k': (105, 100, 90),
}
_STONE_ROAD = [
    "KKKKkKKKkKKKkKKK",
    "KLLMkKMLLMkKMLLM",
    "KLLMkKMLLMkKMLLM",
    "KLLMkKMLLMkKMLLM",
    "KKKKkKKKkKKKkKKK",
    "KMLLLkKMLLLkKMLL",
    "KMLLLkKMLLLkKMLL",
    "KMLLLkKMLLLkKMLL",
    "KKKKkKKKkKKKkKKK",
    "KLLMkKMLLMkKMLLM",
    "KLLMkKMLLMkKMLLM",
    "KLLMkKMLLMkKMLLM",
    "KKKKkKKKkKKKkKKK",
    "KMLLLkKMLLLkKMLL",
    "KMLLLkKMLLLkKMLL",
    "KKKKkKKKkKKKkKKK",
]

# ─────────────────────────────────────────────────────────────────────
#  AREIA
# ─────────────────────────────────────────────────────────────────────
_SAND_P = {
    'Y': (210, 190, 100), 'y': (185, 163, 72),
    'W': (235, 218, 130), 'w': (248, 232, 158),
    'd': (165, 142, 55),
}
_SAND = [
    "YYyYYYYyYYYyYYYY",
    "YWYYwYYYYwYYYYwY",
    "YYYYYyYYYYYYYYYY",
    "yYYYYYYYyYYyYYYY",
    "YYwYYYYYYYYYwYYY",
    "YYYYYyYYYYYYYYyY",
    "WYYYYYYwYYYYYYYW",
    "YYYdYYYYYYdYYYYY",
    "YYYYYYYYYYYYYYYY",
    "YyYYwYYYyYYYwYYY",
    "YYYYYYyYYYYYYYYy",
    "wYYYYYYYwYYYYYYY",
    "YYdYYYYYYYdYYYYY",
    "YYYYyYYYYYYYYyYY",
    "WYYYYYYwYYYYYYYW",
    "YYYYYYYYYYYYYYYY",
]

# ─────────────────────────────────────────────────────────────────────
#  CINZA / FUMAÇA (AshTile)
# ─────────────────────────────────────────────────────────────────────
_ASH_P = {
    'A': (140, 130, 120), 'a': (118, 108, 98),
    'l': (162, 152, 145), 'd': (82, 72, 64),
}
_ASH = [
    "AaAAaAAaAaAAaAAa",
    "AAAlAAAAAAAAlAAA",
    "AAdAAdAAdAAdAAdA",
    "AAAAAAAAdAAAAdAA",
    "aAAlAAaAAlAAaAAl",
    "AAAdAAAAAdAAAAA",
    "AAAAAAAdAAAAAAAA",
    "AlAAAAlAAAAlAAAA",
    "AAAaAAAaAAaAAAAa",
    "AdAAAdAAAAAAAAdA",
    "AAAAlAAAAAlAAAAA",
    "AAAAAAAAAAAAAAaA",
    "AAlAAAlAAAAlAAAA",
    "AAAAAAAaAAAAaAAA",
    "AdAAdAAAAAAAAdAA",
    "AAAAAAAAAAAAAAAA",
]

# ─────────────────────────────────────────────────────────────────────
#  ROCHA VULCÂNICA (HotRockTile)
# ─────────────────────────────────────────────────────────────────────
_HOT_ROCK_P = {
    'D': (52, 32, 20), 'd': (72, 46, 28),
    'R': (92, 58, 36), 'O': (200, 78, 0),
    'o': (235, 125, 18), 'K': (28, 16, 8),
}
_HOT_ROCK = [
    "DDdDDDDdDDDdDDDD",
    "DdDDdDDDDdDDDdDD",
    "DDDDDdDDDDDDDDdD",
    "DDOooODDDDOooODD",
    "DDoOodDDDdoOodDD",
    "DDDooODDDDDooODD",
    "DdDDDDdDDdDDDDdD",
    "DDDDdDDDDDDdDDDD",
    "DOooODDDDOooODDD",
    "DoOodDDdoOoodDDD",
    "DDooODDDDooODDDD",
    "DdDDDDdDdDDDDDdD",
    "DDDdDDDDDDdDDDDD",
    "DDDDDdDDDDDDDdDD",
    "dDDDDDdDDDDDDDdD",
    "DDDDDDDDDDDDDDDD",
]

# ─────────────────────────────────────────────────────────────────────
#  PONTE DE MADEIRA (WoodBridgeTile)
# ─────────────────────────────────────────────────────────────────────
_BRIDGE_P = {
    'W': (148, 92, 42), 'w': (128, 76, 30),
    'D': (98, 58, 18),  'K': (68, 38, 8),
    'B': (20, 80, 178), 'b': (35, 100, 195),
}
_BRIDGE = [
    "BbbBBbBBbBBbBBbB",
    "KKKKKKKKKKKKKKkk",
    "KWwWwWwWwWwWwWwK",
    "KWwWwWwWwWwWwWwK",
    "KDdDdDdDdDdDdDdK",
    "KWwWwWwWwWwWwWwK",
    "KWwWwWwWwWwWwWwK",
    "KKKKKKKKKKKKKKkk",
    "BbbBBbBBbBBbBBbB",
    "KKKKKKKKKKKKKKkk",
    "KWwWwWwWwWwWwWwK",
    "KWwWwWwWwWwWwWwK",
    "KDdDdDdDdDdDdDdK",
    "KWwWwWwWwWwWwWwK",
    "KWwWwWwWwWwWwWwK",
    "KKKKKKKKKKKKKKkk",
]

# ─────────────────────────────────────────────────────────────────────
#  REGISTRO  chave → lista de frames (pixels, palette)
# ─────────────────────────────────────────────────────────────────────
_TILE_DATA: dict[str, list[tuple]] = {
    "grass":       [(_GRASS,      _GRASS_P)],
    "water":       [(_WATER_F0,   _WATER_P), (_WATER_F1, _WATER_P)],
    "rock":        [(_ROCK,       _ROCK_P)],
    "flower_grass":[(_FLOWER,     _FLOWER_P)],
    "bush":        [(_BUSH,       _BUSH_P)],
    "tree":        [(_TREE,       _TREE_P)],
    "wood_path":   [(_WOOD_PATH,  _WOOD_P)],
    "stone_road":  [(_STONE_ROAD, _STONE_ROAD_P)],
    "sand":        [(_SAND,       _SAND_P)],
    "ash":         [(_ASH,        _ASH_P)],
    "hot_rock":    [(_HOT_ROCK,   _HOT_ROCK_P)],
    "wood_bridge": [(_BRIDGE,     _BRIDGE_P)],
}

# Cache (chave, frame) → Surface 32×32
_cache: dict[tuple[str, int], pygame.Surface] = {}


def get_tile_sprite(tile_key: str, frame: int = 0) -> "pygame.Surface | None":
    """Retorna Surface 32×32 ou None se chave/frame não existe."""
    data = _TILE_DATA.get(tile_key)
    if not data:
        return None
    frame = frame % len(data)
    cache_k = (tile_key, frame)
    if cache_k not in _cache:
        pixels, palette = data[frame]
        _cache[cache_k] = _build(pixels, palette)
    return _cache[cache_k]


def get_tile_frame_count(tile_key: str) -> int:
    """Número de frames para animação do tile (1 = estático)."""
    data = _TILE_DATA.get(tile_key)
    return len(data) if data else 0
