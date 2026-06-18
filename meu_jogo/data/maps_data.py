"""
meu_jogo/data/maps_data.py

Mapas baseados em imagem (PNG):
- MUNDO_ABERTO: overworld rolante (mapa.png). Interior andável, borda bloqueia,
  5 santuários (portais) alinhados aos santuários pintados.
- ARENA_*: salas andáveis com vista de cima (area*.png). Andar até o altar
  central inicia a batalha contra o boss daquele elemento.

A batalha em si é uma cena sobreposta (BattleScene), disparada quando o
destino de um portal é uma chave de ROOM_BOSS (ver characters_data).
"""

from meu_jogo.core.map import GameMap, Tile, WallTile, PortalTile
from meu_jogo.data.characters_data import slime, goblin, wolf, forest_guardian

# Compatibilidade com o fluxo antigo de Game
map1 = GameMap("Floresta", enemies=[slime, goblin, wolf], boss=forest_guardian)
maps = [map1]


# Tiles compartilhados (no modo imagem-mundo o chão não é desenhado;
# só importa se é caminhável).
_WALL   = WallTile()
_GROUND = Tile("Campo", "None", (50, 90, 50), True, 0)

_HUB_X, _HUB_Y = 20, 25   # ponto de retorno no overworld


# -----------------------------------------------------------------------
# OVERWORLD — imagem rolante (mapa.png)
# -----------------------------------------------------------------------
def _build_overworld_matrix():
    size = 40
    m = [["X" if (r in (0, size - 1) or c in (0, size - 1)) else " "
          for c in range(size)] for r in range(size)]
    m[5][20]  = "W"   # Norte  → Vento
    m[35][20] = "E"   # Sul    → Elétrico
    m[20][34] = "F"   # Leste  → Fogo
    m[20][5]  = "A"   # Oeste  → Água
    m[20][20] = "^"   # Centro → Sombra
    return m


MUNDO_ABERTO_MATRIX = _build_overworld_matrix()

# Portais do overworld levam às arenas andáveis (spawn na entrada da arena).
_ARENA_ENTRY = (13, 11)
OVERWORLD_TILE_TYPES = {
    "X": _WALL,
    " ": _GROUND,
    "W": PortalTile("Santuário do Vento",    (120, 190, 230), "ARENA_VENTO",    *_ARENA_ENTRY),
    "A": PortalTile("Santuário da Água",     ( 20, 100, 220), "ARENA_AGUA",     *_ARENA_ENTRY),
    "E": PortalTile("Santuário Elétrico",    (200, 180,   0), "ARENA_ELETRICA", *_ARENA_ENTRY),
    "F": PortalTile("Santuário do Fogo",     (220,  60,   0), "ARENA_FOGO",     *_ARENA_ENTRY),
    "^": PortalTile("Santuário das Sombras", (140,  50, 200), "ARENA_SOMBRA",   *_ARENA_ENTRY),
}


# -----------------------------------------------------------------------
# ARENAS — salas andáveis com vista de cima (area*.png)
# -----------------------------------------------------------------------
def _build_arena(world_image, boss_room_key, altar_color):
    cols, rows = 26, 16
    m = [["X" if (r in (0, rows - 1) or c in (0, cols - 1)) else " "
          for c in range(cols)] for r in range(rows)]
    m[4][13]  = "Z"   # altar central → inicia a batalha
    m[13][3]  = "O"   # saída → volta ao overworld
    tile_types = {
        "X": _WALL,
        " ": _GROUND,
        "Z": PortalTile("Altar de Batalha", altar_color, boss_room_key, 0, 0),
        "O": PortalTile("Saída", (50, 210, 100), "MUNDO_ABERTO", _HUB_X, _HUB_Y),
    }
    return {"matrix": m, "tile_types": tile_types, "world_image": world_image}


ARENA_AGUA     = _build_arena("areaagua.png",  "SALA_BATALHA_AGUA",     ( 40, 140, 255))
ARENA_FOGO     = _build_arena("areafogo.png",  "SALA_BATALHA_FOGO",     (255,  90,  30))
ARENA_VENTO    = _build_arena("areaar.png",    "SALA_BATALHA_VENTO",    (190, 230, 255))
ARENA_ELETRICA = _build_arena("areaterra.png", "SALA_BATALHA_ELETRICA", (255, 235,  60))
ARENA_SOMBRA   = _build_arena("finalarena.png","SALA_BATALHA_SOMBRA",   (170,  80, 240))


# -----------------------------------------------------------------------
# Dicionário geral de mapas
# -----------------------------------------------------------------------
ALL_MAP_DATA = {
    "MUNDO_ABERTO": {
        "matrix":     MUNDO_ABERTO_MATRIX,
        "tile_types": OVERWORLD_TILE_TYPES,
        "world_image": "mapa.png",
    },
    "ARENA_AGUA":     ARENA_AGUA,
    "ARENA_FOGO":     ARENA_FOGO,
    "ARENA_VENTO":    ARENA_VENTO,
    "ARENA_ELETRICA": ARENA_ELETRICA,
    "ARENA_SOMBRA":   ARENA_SOMBRA,
}


# -----------------------------------------------------------------------
# Regiões para notificações de área (coordenadas col, row do overworld 40×40)
# -----------------------------------------------------------------------
REGIONS = {
    "ceu_ventos": {
        "name": "Céu dos Ventos",
        "color": (180, 220, 255),
        "tiles": [(c, r) for c in range(1, 39) for r in range(1, 13)],
    },
    "terra_trovejante": {
        "name": "Terra Trovejante",
        "color": (220, 200, 50),
        "tiles": [(c, r) for c in range(1, 39) for r in range(27, 39)],
    },
    "vulcao": {
        "name": "Vulcão Ardente",
        "color": (255, 100, 30),
        "tiles": [(c, r) for c in range(27, 39) for r in range(13, 27)],
    },
    "caverna_aguas": {
        "name": "Caverna das Águas",
        "color": (80, 180, 255),
        "tiles": [(c, r) for c in range(1, 13) for r in range(13, 27)],
    },
    "centro": {
        "name": "Clareira Central",
        "color": (100, 200, 100),
        "tiles": [(c, r) for c in range(13, 27) for r in range(13, 27)],
    },
}
