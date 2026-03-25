import pygame
from meu_jogo.core.map import (
    GameMap, Tile, GrassTile, WaterTile, FireTile,
    WindTile, WallTile, PortalTile,
)
from meu_jogo.data.characters_data import (
    slime, goblin, wolf, forest_guardian,
    hydra, thunder_beast, storm_eagle, magma_titan,
    ROOM_BOSS,
)

# Compatibilidade com Game original
map1 = GameMap("Floresta", enemies=[slime, goblin, wolf], boss=forest_guardian)
maps = [map1]


# -----------------------------------------------------------------------
# Tiles customizados
# -----------------------------------------------------------------------
class ElectricFloorTile(Tile):
    def __init__(self):
        super().__init__("Chão Elétrico", "Electric", (200, 170, 0), True, 0)

class WindFloorTile(Tile):
    def __init__(self):
        super().__init__("Chão Vento", "Air", (160, 210, 230), True, 0)

class PathTile(Tile):
    """Caminho de terra/pedra — cor neutra para corredores."""
    def __init__(self):
        super().__init__("Caminho", "None", (160, 130, 90), True, 0)

class DirtTile(Tile):
    def __init__(self):
        super().__init__("Terra", "None", (120, 85, 50), True, 0)


# -----------------------------------------------------------------------
# Tiles globais
# -----------------------------------------------------------------------
GLOBAL_TILE_TYPES = {
    "G": GrassTile(),           # Verde escuro
    "g": Tile("Grama Clara", "Grass", (90, 180, 80), True, 0),
    "P": WaterTile(),           # Azul água
    "B": FireTile(),            # Vermelho fogo
    "V": WindTile(),            # Azul-claro vento
    "X": WallTile(),            # Marrom parede/montanha
    "D": DirtTile(),            # Terra marrom
    "C": PathTile(),            # Caminho bege
    " ": GrassTile(),

    # Portais (entradas das salas)
    "A": PortalTile("Portal Água",    (20, 100, 220),  "SALA_BATALHA_AGUA",     1, 1),
    "E": PortalTile("Portal Elétrico",(200, 180,  0),  "SALA_BATALHA_ELETRICA", 1, 1),
    "W": PortalTile("Portal Vento",   (120, 190, 230), "SALA_BATALHA_VENTO",    1, 1),
    "F": PortalTile("Portal Fogo",    (220,  60,  0),  "SALA_BATALHA_FOGO",     1, 1),
    "O": PortalTile("Saída",          ( 50, 210, 100), "MUNDO_ABERTO",         10, 7),
}

# Tiles das salas internas
WATER_ROOM_TILES  = {**GLOBAL_TILE_TYPES,
    "P": WaterTile(name="Fundo Aquático", color=(20, 90, 200)),
    "O": PortalTile("Saída", (50, 210, 100), "MUNDO_ABERTO", 10, 7),
}
ELEC_ROOM_TILES   = {**GLOBAL_TILE_TYPES,
    "E": ElectricFloorTile(),
    "O": PortalTile("Saída", (50, 210, 100), "MUNDO_ABERTO", 10, 7),
}
WIND_ROOM_TILES   = {**GLOBAL_TILE_TYPES,
    "V": WindFloorTile(),
    "O": PortalTile("Saída", (50, 210, 100), "MUNDO_ABERTO", 10, 7),
}
FIRE_ROOM_TILES   = {**GLOBAL_TILE_TYPES,
    "B": FireTile(name="Lava", color=(210, 50, 0), damage=8),
    "O": PortalTile("Saída", (50, 210, 100), "MUNDO_ABERTO", 10, 7),
}


# -----------------------------------------------------------------------
# MUNDO ABERTO 20×20
# Layout:
#   Topo   centro → sala VENTO  (W azul-claro)
#   Meio   esquerda → sala ÁGUA (A azul)
#   Meio   direita  → sala ELÉTRICA (E amarelo)
#   Base   centro → sala FOGO  (F vermelho)
#   Centro do mapa → grama verde (sem azul)
# -----------------------------------------------------------------------
W = "W"  # portal vento
A = "A"  # portal água
E = "E"  # portal elétrico
F = "F"  # portal fogo
X = "X"  # parede
G = "G"  # grama
g = "g"  # grama clara
P = "P"  # água
B = "B"  # fogo/brasa
V = "V"  # vento
C = "C"  # caminho
D = "D"  # terra

MUNDO_ABERTO_MATRIX = [
#   0    1    2    3    4    5    6    7    8    9   10   11   12   13   14   15   16   17   18   19
   [X,   X,   X,   X,   X,   X,   X,   X,   X,   X,   X,   X,   X,   X,   X,   X,   X,   X,   X,   X],  # 0
   [X,   P,   P,   D,   X,   V,   V,   V,   V,  "W",  V,   V,   V,   V,   X,   E,   E,   D,   X,   X],  # 1
   [X,   P,   P,   D,   X,   V,   V,   V,   V,   V,   V,   V,   V,   V,   X,   E,   E,   D,   X,   X],  # 2
   [X,   P,   P,   D,   C,   C,   C,   C,  "W",  C,   C,   C,   C,   C,   C,   E,   E,   D,   X,   X],  # 3  ← portal vento linha 3 col 8
   [X,   P,   P,   D,   G,   G,   G,   G,   G,   G,   G,   G,   G,   G,   G,   E,   E,   D,   X,   X],  # 4
   [X,   X,   X,   D,   G,   X,   X,   X,   X,   X,   X,   X,   X,   X,   G,   X,   X,   D,   X,   X],  # 5
   [X,   P,   P,   G,   G,   g,   g,   g,   g,   g,   g,   g,   g,   g,   G,   E,   E,   G,   E,   X],  # 6
   [X,  "A",  P,   G,   G,   g,   g,   g,   g,   g,   g,   g,   g,   g,   G,   E,  "E",  G,   E,   X],  # 7  ← portais laterais
   [X,   P,   P,   G,   G,   g,   g,   g,   g,   g,   g,   g,   g,   g,   G,   E,   E,   G,   E,   X],  # 8
   [X,   X,   X,   D,   G,   X,   X,   X,   X,   X,   X,   X,   X,   X,   G,   X,   X,   D,   X,   X],  # 9
   [X,   P,   P,   D,   G,   G,   G,   G,   G,   G,   G,   G,   G,   G,   G,   E,   E,   D,   X,   X],  # 10
   [X,   P,   P,   D,   C,   C,   C,   C,  "F",  C,   C,   C,   C,   C,   C,   E,   E,   D,   X,   X],  # 11 ← portal fogo
   [X,   P,   P,   D,   X,   B,   B,   B,   B,   B,   B,   B,   B,   B,   X,   E,   E,   D,   X,   X],  # 12
   [X,   P,   P,   D,   X,   B,   B,   B,   B,   B,   B,   B,   B,   B,   X,   E,   E,   D,   X,   X],  # 13
   [X,   X,   X,   X,   X,   X,   X,   X,   X,   X,   X,   X,   X,   X,   X,   X,   X,   X,   X,   X],  # 14
]


# -----------------------------------------------------------------------
# Salas de batalha 7×7
# -----------------------------------------------------------------------
def _room(floor: str, has_damage_floor=False):
    f = floor
    return [
        [X, X, X, X, X, X, X],
        [X, f, f, f, f, f, X],
        [X, f, f, f, f, f, X],
        [X, f, f,"O", f, f, X],
        [X, f, f, f, f, f, X],
        [X, f, f, f, f, f, X],
        [X, X, X, X, X, X, X],
    ]

SALA_BATALHA_AGUA_MATRIX     = _room("P")
SALA_BATALHA_ELETRICA_MATRIX = _room("E")
SALA_BATALHA_VENTO_MATRIX    = _room("V")
SALA_BATALHA_FOGO_MATRIX     = _room("B")


# -----------------------------------------------------------------------
# Dicionário geral
# -----------------------------------------------------------------------
ALL_MAP_DATA = {
    "MUNDO_ABERTO": {
        "matrix":     MUNDO_ABERTO_MATRIX,
        "tile_types": GLOBAL_TILE_TYPES,
    },
    "SALA_BATALHA_AGUA": {
        "matrix":     SALA_BATALHA_AGUA_MATRIX,
        "tile_types": WATER_ROOM_TILES,
    },
    "SALA_BATALHA_ELETRICA": {
        "matrix":     SALA_BATALHA_ELETRICA_MATRIX,
        "tile_types": ELEC_ROOM_TILES,
    },
    "SALA_BATALHA_VENTO": {
        "matrix":     SALA_BATALHA_VENTO_MATRIX,
        "tile_types": WIND_ROOM_TILES,
    },
    "SALA_BATALHA_FOGO": {
        "matrix":     SALA_BATALHA_FOGO_MATRIX,
        "tile_types": FIRE_ROOM_TILES,
    },
}