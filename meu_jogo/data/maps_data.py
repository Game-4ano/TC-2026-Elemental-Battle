import pygame
from meu_jogo.core.map import (
    Tile, GrassTile, WaterTile, FireTile,
    WindTile, WallTile, PortalTile,
    # Água
    IceTile, CrystalTile, RiverTile, WetSandTile,
    # Fogo
    LavaTile, HotRockTile, AshTile, EmberTile,
    # Vento
    CloudTile, SkyPathTile, WindyGrassTile, FeatherTile,
    # Elétrico
    SandTile, ChargedSandTile, MetalTile, LightningCrystalTile,
    # Centro
    FlowerGrassTile, BushTile, TreeTile, WoodPathTile,
    # Caminhos
    StoneRoadTile, WoodBridgeTile,
    # Arenas
    IceArenaTile, VolcanoFloorTile, SkyArenaTile, MetalArenaTile, ForestArenaTile,
    DeepWaterTile, SkyVoidTile,
    # Decorativos de sala
    IceStalactiteTile, BubbleTile, LavaDropTile, CircuitFloorTile, NeonBorderTile,
    # Sombra
    VoidFloorTile, ShadowCrystalTile, DarkMistTile, TwilightTile,
    # Decorações ambientais do mundo aberto
    MushroomTile, BoneTile, BoltTile,
)
from meu_jogo.core.map_builder import build_themed_room, make_room_tiles

# -----------------------------------------------------------------------
# Aliases curtos para a matriz
# -----------------------------------------------------------------------
X  = "X"   # WallTile
G  = "G"   # GrassTile
g  = "g"   # FlowerGrassTile
P  = "P"   # WaterTile (lago/rio decorativo sem dano)
R  = "R"   # RiverTile (rio com dano leve)
C  = "C"   # PathTile / StoneRoadTile
D  = "D"   # DirtTile
M  = "M"   # WoodPathTile
T  = "T"   # TreeTile
B2 = "b"   # BushTile
# Água
I  = "I"   # IceTile
Y  = "Y"   # CrystalTile (azul, não-caminhável)
S  = "S"   # WetSandTile
# Fogo
L  = "L"   # LavaTile
H  = "H"   # HotRockTile
Q  = "Q"   # AshTile
K  = "K"   # EmberTile
# Vento
U  = "U"   # CloudTile
Z  = "Z"   # SkyPathTile
J  = "J"   # WindyGrassTile
N  = "N"   # FeatherTile
# Elétrico
A2 = "d"   # SandTile
E2 = "e"   # ChargedSandTile
V2 = "v"   # MetalTile
O2 = "o"   # LightningCrystalTile (não-caminhável)
# Portais
WP = "W"   # Portal Vento
AP = "A"   # Portal Água
EP = "E"   # Portal Elétrico
FP = "F"   # Portal Fogo
OP = "O"   # Saída (volta ao mundo aberto)


# -----------------------------------------------------------------------
# Tiles globais
# -----------------------------------------------------------------------
GLOBAL_TILE_TYPES = {
    "X": WallTile(),
    "G": GrassTile(),
    "g": FlowerGrassTile(),
    "P": WaterTile(name="Lago", color=(30, 100, 200), damage=0),
    "R": RiverTile(),
    "C": StoneRoadTile(),
    "D": Tile("Terra", "None", (120, 85, 50), True, 0),
    "M": WoodPathTile(),
    "T": TreeTile(),
    "b": BushTile(),
    # Água
    "I": IceTile(),
    "Y": CrystalTile(),
    "S": WetSandTile(),
    # Fogo
    "L": LavaTile(),
    "H": HotRockTile(),
    "Q": AshTile(),
    "K": EmberTile(),
    # Vento
    "U": CloudTile(),
    "Z": SkyPathTile(),
    "J": WindyGrassTile(),
    "N": FeatherTile(),
    # Elétrico
    "d": SandTile(),
    "e": ChargedSandTile(),
    "v": MetalTile(),
    "o": LightningCrystalTile(),
    # Portais
    "W": PortalTile("Portal Vento",    (120, 190, 230), "SALA_BATALHA_VENTO",    pygame.Vector2(1, 1)),
    "A": PortalTile("Portal Água",     ( 20, 100, 220), "SALA_BATALHA_AGUA",     pygame.Vector2(1, 1)),
    "E": PortalTile("Portal Elétrico", (200, 180,   0), "SALA_BATALHA_ELETRICA", pygame.Vector2(1, 1)),
    "F": PortalTile("Portal Fogo",     (220,  60,   0), "SALA_BATALHA_FOGO",     pygame.Vector2(1, 1)),
    "O": PortalTile("Saída",           ( 50, 210, 100), "MUNDO_ABERTO",         pygame.Vector2(20, 14)),
    "^": PortalTile("Portal Sombra",   (140,  50, 200), "SALA_BATALHA_SOMBRA",   pygame.Vector2(1, 1)),
    "%": PortalTile("Portal Planta",   ( 60, 200,  60), "SALA_BATALHA_PLANTA",   pygame.Vector2(1, 1)),
    # Degrade Vazio Sombrio -> Ceu dos Ventos (3 colunas de transicao)
    "1": TwilightTile(0.25),
    "2": TwilightTile(0.5),
    "3": TwilightTile(0.75),
    # Clareira sombria (moldura do portal Sombra, para nao ficar solto entre nuvens)
    "!": VoidFloorTile(),
    "~": DarkMistTile(),
    # Decorações ambientais do mundo aberto
    "q": ShadowCrystalTile(),   # cristal sombrio perto do portal sombra
    "m": MushroomTile(),        # cogumelo perto da água (oeste)
    "f": BoneTile(),            # osso carbonizado perto do fogo (leste)
    "j": BoltTile(),            # parafuso metálico perto do elétrico (sul)
    " ": GrassTile(),
}

# -----------------------------------------------------------------------
# MUNDO ABERTO 40×30
# Layout:
#   Linhas  0- 7 → NORTE (Céu dos Ventos)
#   Linhas  8-11 → corredor norte-centro
#   Linhas 12-18 → CENTRO (vila/clareira)
#   Linhas 19-22 → corredor sul-centro
#   Linhas 23-29 → SUL (Terra Trovejante)
#   Colunas 0- 8 → OESTE (Caverna das Águas)
#   Colunas 9-30 → centro/leste
#   Colunas 31-39 → LESTE (Vulcão)
# Portal Vento   → col 20, lin 1
# Portal Água    → col 1,  lin 15
# Portal Elétrico→ col 20, lin 28
# Portal Fogo    → col 38, lin 15
# -----------------------------------------------------------------------

# Cada linha tem 40 colunas (índices 0–39)
MUNDO_ABERTO_MATRIX = [
# col: 0   1   2   3   4   5   6   7   8   9  10  11  12  13  14  15  16  17  18  19  20  21  22  23  24  25  26  27  28  29  30  31  32  33  34  35  36  37  38  39
# REGIÃO NORTE — Céu dos Ventos (lin 0-7)
  [X,  X,  X,  X,  X,  X,  X,  X,  X,  X,  X,  X,  X,  X,  X,  X,  X,  X,  X,  X,  X,  X,  X,  X,  X,  X,  X,  X,  X,  X,  X,  X,  X,  X,  X,  X,  X,  X,  X,  X], # 0
  [X, "q", "!", "!", "!", "!", "!", "!", "q", "!", "!", "!", "!", "!", "q", "1", "2", "3",  U,  U, "W", U,  U,  U,  U,  U,  U,  U,  U,  U,  U,  X,  X,  X,  X,  X,  X,  X,  X,  X], # 1 ← Portal Vento
  [X, "!", "!", "!", "!", "!", "!", "~", "!", "!", "!", "!", "!", "!", "~", "1", "2", "3",  U,  U,  U,  U,  J,  N,  U,  U,  J,  U,  U,  U,  U,  X,  X,  X,  X,  X,  X,  X,  X,  X], # 2
  [X, "!", "q", "!", "!", "^", "!", "!", "!", "!", "!", "!", "!", "!", "!", "1", "2", "3",  Z,  Z,  Z,  Z,  J,  J,  Z,  Z,  J,  Z,  U,  U,  U,  X,  X,  X,  X,  X,  X,  X,  X,  X], # 3 ← Portal Sombra
  [X, "!", "!", "~", "!", "!", "!", "!", "q", "!", "!", "!", "!", "q", "!", "1", "2", "3",  U,  Z,  U,  Z,  J,  J,  U,  Z,  J,  Z,  U,  U,  U,  X,  X,  X,  X,  X,  X,  X,  X,  X], # 4
  [X, "!", "!", "!", "q", "!", "!", "~", "!", "!", "!", "!", "!", "!", "!", "1", "2", "3",  U,  Z,  U,  Z,  U,  U,  U,  Z,  U,  Z,  U,  U,  U,  X,  X,  X,  X,  X,  X,  X,  X,  X], # 5
  [X,  U,  U,  C,  C,  C,  C,  C,  C,  C,  C,  C,  C,  C,  C,  C,  C,  C,  C,  C,  C,  C,  C,  C,  C,  C,  C,  C,  C,  U,  U,  X,  X,  X,  X,  X,  X,  X,  X,  X], # 6 ← corredor norte
  [X,  U,  U,  C,  U,  U,  U,  U,  U,  U,  U,  U,  U,  U,  U,  U,  U,  U,  U,  U,  U,  U,  U,  U,  U,  U,  U,  U,  C,  U,  U,  X,  X,  X,  X,  X,  X,  X,  X,  X], # 7

# CORREDOR Norte-Centro (lin 8-11)
  [X,  G, "m",  C,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  C,  G,  G,  X,  X,  H,  H,  X,  X,  X,  X,  X], # 8
  [X,  G, "m",  C,  G,  T,  G,  G,  G,  G,  T,  G,  G,  G,  G,  T,  G,  G,  G,  G,  T,  G,  G,  G,  G,  G,  G,  G,  C,  G,  G,  X,  H,  H,  H, "f",  X,  X,  X,  X], # 9
  [X,  R,  R,  C,  G, "b", G,  G,  G, "b", G,  G, "b", G,  G,  G, "b", G,  G,  G,  G,  G, "b", G,  G,  G,  G,  G,  C,  G,  G,  H,  H,  Q,  Q,  H,  H,  X,  X,  X], # 10
  [X,  P,  P,  C,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  C,  G,  G,  H,  Q,  Q,  Q,  Q,  H,  X,  X,  X], # 11

# CENTRO — Vila/Clareira (lin 12-18)
  [X,  P,  P,  M,  g,  g,  g,  g,  g,  g,  g,  g,  g,  g,  g,  g,  g,  g,  g,  g,  g,  g,  g,  g,  g,  g,  g,  g,  M,  g,  g,  H,  Q,  L,  L,  Q,  H,  X,  X,  X], # 12
  [X,  P,  P,  M,  g,  T,  g,  g,  g,  g,  T,  g,  g,  g,  g,  T,  g,  g,  g,  g,  T,  g,  g,  g,  g,  g,  g,  g,  M,  g,  g,  H,  K,  L,  L,  K,  H,  X,  X,  X], # 13
  [X, "A", P,  M,  g,  g,  g,  g,  g,  g,  g,  g,  g,  g,  g,  g,  g,  g,  g,  g,  g,  g,  g,  g,  g,  g,  g,  g,  M,  g,  g,  H,  K,  L,  L,  K, "F", X,  X,  X], # 14 ← Portal Água/Fogo
  [X,  P,  R,  M,  g,  g, "b", g,  g, "b", g,  g, "b", g,  g,  g, "b", g,  g,  g,  g,  g, "b", g,  g,  g,  g,  g,  M,  g,  g,  H,  K,  L,  L,  K,  H,  X,  X,  X], # 15
  [X,  P,  P,  M,  g,  g,  g,  g,  g,  g,  g,  g,  g,  g,  g, "%",  g,  g,  g,  g,  g,  g,  g,  g,  g,  g,  g,  g,  M,  g,  g,  H,  Q,  L,  L,  Q,  H,  X,  X,  X], # 16 ← Portal Planta
  [X,  P,  P,  M,  g,  T,  g,  g,  g,  g,  T,  g,  g,  g,  g,  T,  g,  g,  g,  g,  T,  g,  g,  g,  g,  g,  g,  g,  M,  g,  g,  H, "f",  Q,  Q,  H,  H,  X,  X,  X], # 17
  [X,  P,  P,  M,  g,  g,  g,  g,  g,  g,  g,  g,  g,  g,  g,  g,  g,  g,  g,  g,  g,  g,  g,  g,  g,  g,  g,  g,  M,  g,  g,  X,  H,  H,  H,  H,  X,  X,  X,  X], # 18

# CORREDOR Centro-Sul (lin 19-22)
  [X,  P,  P,  C,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  C,  G,  G,  X,  X,  H,  H,  X,  X,  X,  X,  X], # 19
  [X,  R,  P,  C,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  C,  G,  G,  X,  X,  X,  X,  X,  X,  X,  X,  X], # 20
  [X,  P,  P,  C,  G,  T,  G,  G,  G,  G,  T,  G,  G,  G,  G,  T,  G,  G,  G,  G,  T,  G,  G,  G,  G,  G,  G,  G,  C,  G,  G,  X,  X,  X,  X,  X,  X,  X,  X,  X], # 21
  [X,  P,  I,  C,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  G,  C,  G,  G,  X,  X,  X,  X,  X,  X,  X,  X,  X], # 22

# REGIÃO SUL — Terra Trovejante (lin 23-29)
  [X,  I,  I,  C,  "d","d","d","d","d","d","d","d","d","d","d","d","d","d","d","d","e","d","d","d","d","d","d","d", C, "d","d", X,  X,  X,  X,  X,  X,  X,  X,  X], # 23
  [X,  I,  I, "d","d","e","d","d","d","d","j","d","e","d","d","d","d","d","d","d","e","d","d","d","e","d","d","d","d","d","d", X,  X,  X,  X,  X,  X,  X,  X,  X], # 24
  [X,  Y,  I, "d","d","d","d","o","d","d","d","d","d","o","d","d","d","d","d","d","d","d","d","d","d","o","d","d","d","d","d", X,  X,  X,  X,  X,  X,  X,  X,  X], # 25
  [X,  I,  I, "d","e","d","d","d","d","d","d","d","e","d","d","d","d","d","d","d","E","d","d","d","d","d","d","d","e","d","d", X,  X,  X,  X,  X,  X,  X,  X,  X], # 26 ← Portal Elétrico col 20
  [X,  I,  I, "d","d","d","d","d","d","d","d","d","d","d","d","d","d","d","j","d","e","d","d","d","d","d","d","d","d","d","d", X,  X,  X,  X,  X,  X,  X,  X,  X], # 27
  [X,  I,  I, "d","d","e","d","d","d","d","o","d","d","d","d","o","d","d","d","d","e","d","d","d","d","o","d","d","d","d","d", X,  X,  X,  X,  X,  X,  X,  X,  X], # 28
  [X,  X,  X,  X,  X,  X,  X,  X,  X,  X,  X,  X,  X,  X,  X,  X,  X,  X,  X,  X,  X,  X,  X,  X,  X,  X,  X,  X,  X,  X,  X,  X,  X,  X,  X,  X,  X,  X,  X,  X], # 29
]

# Região OESTE — Caverna das Águas (cols 0-2, já integradas acima)
# mas vamos completar o mapa de água como overlay usando as colunas 0-2
# As linhas 22-28 do oeste têm tiles I/Y  (IceTile/CrystalTile)
# As linhas 8-11 do corredor têm R/P


# -----------------------------------------------------------------------
# Salas de batalha 12×10  (montadas por core.map_builder.build_themed_room)
# -----------------------------------------------------------------------


# --- SALA ÁGUA (Hydra) — Caverna Submersa ---
_AGUA_DECO = [
    # Água profunda nas bordas internas
    (1, 1,"w"), (1,10,"w"), (8, 1,"w"), (8,10,"w"),
    (1, 2,"w"), (1, 9,"w"), (8, 2,"w"), (8, 9,"w"),
    (2, 1,"w"), (2,10,"w"), (7, 1,"w"), (7,10,"w"),
    # Cristais azuis nos cantos internos
    (2, 2,"Y"), (2, 9,"Y"), (7, 2,"Y"), (7, 9,"Y"),
    # Estalactites no topo (não-caminhável, decorativo)
    (1, 3,"st"), (1, 5,"st"), (1, 7,"st"), (1, 9,"st"),
    # Bolhas animadas nas bordas laterais
    (2, 1,"bb"), (4, 1,"bb"), (6, 1,"bb"), (8, 1,"bb"),
    (2,10,"bb"), (4,10,"bb"), (6,10,"bb"), (8,10,"bb"),
    # Poça central
    (4, 5,"P"), (4, 6,"P"), (5, 5,"P"), (5, 6,"P"),
]

WATER_ROOM_TILES_BATTLE = {
    "X":  WallTile(),
    "A":  IceArenaTile(),
    "w":  DeepWaterTile(),
    "Y":  CrystalTile(),
    "P":  WaterTile(name="Poça Brilhante", color=(60, 140, 220), damage=0),
    "st": IceStalactiteTile(),
    "bb": BubbleTile(),
    "O":  PortalTile("Saída", (50, 210, 100), "MUNDO_ABERTO", pygame.Vector2(2, 14)),
}
_agua_raw = build_themed_room("A", "X", _AGUA_DECO, 1, 6)
SALA_BATALHA_AGUA_MATRIX = _agua_raw


# --- SALA FOGO (Magma Titan) — Cratera Vulcânica ---
_FOGO_DECO = [
    # Lava transbordando nas bordas
    (1, 1,"L"), (1,10,"L"), (8, 1,"L"), (8,10,"L"),
    (1, 2,"L"), (1, 9,"L"), (8, 2,"L"), (8, 9,"L"),
    (2, 1,"L"), (2,10,"L"), (7, 1,"L"), (7,10,"L"),
    # Rochas vulcânicas centrais
    (4, 5,"H"), (4, 6,"H"), (5, 5,"H"), (5, 6,"H"),
    # Pingos de lava nas bordas superiores (animados)
    (1, 4,"ld"), (1, 6,"ld"), (1, 8,"ld"),
    (8, 4,"ld"), (8, 6,"ld"), (8, 8,"ld"),
    # Brasas espalhadas
    (3, 3,"K"), (3, 8,"K"), (6, 3,"K"), (6, 8,"K"),
    (2, 5,"K"), (7, 6,"K"), (4, 2,"K"), (5, 7,"K"),
]

FIRE_ROOM_TILES_BATTLE = {
    "X":  WallTile(),
    "V":  VolcanoFloorTile(),
    "L":  LavaTile(),
    "H":  HotRockTile(),
    "K":  EmberTile(),
    "ld": LavaDropTile(),
    "O":  PortalTile("Saída", (50, 210, 100), "MUNDO_ABERTO", pygame.Vector2(35, 14)),
}
_fogo_raw = build_themed_room("V", "X", _FOGO_DECO, 8, 6)
SALA_BATALHA_FOGO_MATRIX = _fogo_raw


# --- SALA VENTO (Storm Eagle) — Arena nas Nuvens ---
_VENTO_DECO = [
    # Vazio celeste extenso nas bordas
    (1, 1,"K"), (1,10,"K"), (8, 1,"K"), (8,10,"K"),
    (1, 2,"K"), (1, 9,"K"), (8, 2,"K"), (8, 9,"K"),
    (2, 1,"K"), (2,10,"K"), (7, 1,"K"), (7,10,"K"),
    (1, 3,"K"), (1, 8,"K"), (8, 3,"K"), (8, 8,"K"),
    (2, 2,"K"), (2, 9,"K"), (7, 2,"K"), (7, 9,"K"),
    # Plataformas celestes flutuantes
    (3, 2,"Z"), (3, 9,"Z"), (6, 2,"Z"), (6, 9,"Z"),
    (4, 1,"Z"), (5, 1,"Z"),
    # Penas caindo em grande quantidade
    (2, 4,"N"), (2, 7,"N"), (7, 4,"N"), (7, 7,"N"),
    (4, 2,"N"), (5, 9,"N"), (3, 5,"N"), (6, 6,"N"),
    (4, 8,"N"), (5, 3,"N"),
]

WIND_ROOM_TILES_BATTLE = {
    "X": WallTile(),
    "S": SkyArenaTile(),
    "K": SkyVoidTile(),
    "Z": SkyPathTile(),
    "N": FeatherTile(),
    "O": PortalTile("Saída", (50, 210, 100), "MUNDO_ABERTO", pygame.Vector2(20, 2)),  # col20, row2 — abaixo do portal Vento
}
_vento_raw = build_themed_room("S", "X", _VENTO_DECO, 1, 6)
SALA_BATALHA_VENTO_MATRIX = _vento_raw


# --- SALA ELÉTRICA (Thunder Beast) — Arena Eletro-Industrial ---
_ELEC_DECO = [
    # Tubos de neon nas bordas (não-caminháveis)
    (1, 1,"nb"), (1,10,"nb"), (8, 1,"nb"), (8,10,"nb"),
    (2, 1,"nb"), (2,10,"nb"), (7, 1,"nb"), (7,10,"nb"),
    # Chão de circuito espalhado
    (2, 2,"cf"), (2, 4,"cf"), (2, 6,"cf"), (2, 8,"cf"),
    (7, 3,"cf"), (7, 5,"cf"), (7, 7,"cf"), (7, 9,"cf"),
    (4, 3,"cf"), (5, 8,"cf"),
    # Cristais raio nos cantos internos
    (3, 3,"o"), (3, 8,"o"), (6, 3,"o"), (6, 8,"o"),
    # Areia carregada
    (1, 3,"e"), (1, 7,"e"), (8, 3,"e"), (8, 7,"e"),
    # Placas de metal central
    (4, 5,"v"), (4, 6,"v"), (5, 5,"v"), (5, 6,"v"),
]

ELEC_ROOM_TILES_BATTLE = {
    "X":  WallTile(),
    "M":  MetalArenaTile(),
    "o":  LightningCrystalTile(),
    "e":  ChargedSandTile(),
    "v":  MetalTile(),
    "cf": CircuitFloorTile(),
    "nb": NeonBorderTile(),
    "O":  PortalTile("Saída", (50, 210, 100), "MUNDO_ABERTO", pygame.Vector2(20, 25)),
}
_elec_raw = build_themed_room("M", "X", _ELEC_DECO, 8, 6)
SALA_BATALHA_ELETRICA_MATRIX = _elec_raw


# --- SALA SOMBRA (Shadow Lord) ---
_SOMBRA_DECO = [
    # Cristais de sombra nos cantos internos
    (2, 2,"c"), (2, 9,"c"), (7, 2,"c"), (7, 9,"c"),
    # Cristais centrais
    (4, 4,"c"), (5, 7,"c"),
    # Névoa espalhada
    (1, 4,"m"), (1, 7,"m"), (8, 4,"m"), (8, 7,"m"),
    (3, 5,"m"), (6, 6,"m"), (4, 8,"m"), (5, 3,"m"),
]

SHADOW_ROOM_TILES_BATTLE = {
    "X": WallTile(),
    "v": VoidFloorTile(),
    "c": ShadowCrystalTile(),
    "m": DarkMistTile(),
    "O": PortalTile("Saída", (50, 210, 100), "MUNDO_ABERTO", pygame.Vector2(5, 4)),
}
_sombra_raw = build_themed_room("v", "X", _SOMBRA_DECO, 8, 6)
SALA_BATALHA_SOMBRA_MATRIX = _sombra_raw


# --- SALA PLANTA (Forest Guardian) — Bosque Sagrado ---
_GRAMA_DECO = [
    # Arvores emoldurando a clareira
    (1, 1,"T"), (1,10,"T"), (8, 1,"T"), (8,10,"T"),
    (1, 2,"T"), (1, 9,"T"), (7, 1,"T"), (7,10,"T"),
    (2, 1,"T"), (2,10,"T"),
    # Arbustos espalhados
    (3, 3,"b"), (3, 8,"b"), (6, 3,"b"), (6, 8,"b"),
    (2, 5,"b"), (2, 6,"b"),
    # Grama florida central
    (4, 5,"g"), (4, 6,"g"), (5, 5,"g"), (5, 6,"g"),
    (4, 2,"g"), (5, 9,"g"), (3, 5,"g"), (6, 6,"g"),
]

GRASS_ROOM_TILES_BATTLE = {
    "X": WallTile(),
    "V": ForestArenaTile(),
    "T": TreeTile(),
    "b": BushTile(),
    "g": FlowerGrassTile(),
    "O": PortalTile("Saída", (50, 210, 100), "MUNDO_ABERTO", pygame.Vector2(15, 15)),
}
_grama_raw = build_themed_room("V", "X", _GRAMA_DECO, 8, 6)
SALA_BATALHA_PLANTA_MATRIX = _grama_raw


# -----------------------------------------------------------------------
# Tile types para salas (herdam GLOBAL + sobrescritas)
# -----------------------------------------------------------------------
WATER_ROOM_TILES  = make_room_tiles(GLOBAL_TILE_TYPES, WATER_ROOM_TILES_BATTLE)
FIRE_ROOM_TILES   = make_room_tiles(GLOBAL_TILE_TYPES, FIRE_ROOM_TILES_BATTLE)
WIND_ROOM_TILES   = make_room_tiles(GLOBAL_TILE_TYPES, WIND_ROOM_TILES_BATTLE)
ELEC_ROOM_TILES   = make_room_tiles(GLOBAL_TILE_TYPES, ELEC_ROOM_TILES_BATTLE)
SHADOW_ROOM_TILES = make_room_tiles(GLOBAL_TILE_TYPES, SHADOW_ROOM_TILES_BATTLE)
GRASS_ROOM_TILES  = make_room_tiles(GLOBAL_TILE_TYPES, GRASS_ROOM_TILES_BATTLE)


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
    "SALA_BATALHA_SOMBRA": {
        "matrix":     SALA_BATALHA_SOMBRA_MATRIX,
        "tile_types": SHADOW_ROOM_TILES,
    },
    "SALA_BATALHA_PLANTA": {
        "matrix":     SALA_BATALHA_PLANTA_MATRIX,
        "tile_types": GRASS_ROOM_TILES,
    },
}


# -----------------------------------------------------------------------
# Regiões para notificações de área (Tarefa 4.5)
# -----------------------------------------------------------------------
REGIONS = {
    "caverna_aguas": {
        "name": "Caverna das Águas",
        "color": (80, 180, 255),
        "tiles": [(c, r) for c in range(0, 4) for r in range(8, 23)],
    },
    "vulcao": {
        "name": "Vulcão Ardente",
        "color": (255, 100, 30),
        "tiles": [(c, r) for c in range(31, 40) for r in range(8, 20)],
    },
    "ceu_ventos": {
        "name": "Céu dos Ventos",
        "color": (180, 220, 255),
        "tiles": [(c, r) for c in range(0, 31) for r in range(0, 8)],
    },
    "terra_trovejante": {
        "name": "Terra Trovejante",
        "color": (220, 200, 50),
        "tiles": [(c, r) for c in range(0, 31) for r in range(23, 30)],
    },
    "centro": {
        "name": "Clareira Central",
        "color": (100, 200, 100),
        "tiles": [(c, r) for c in range(3, 31) for r in range(12, 19)],
    },
    # Sub-regioes especificas dos clareiras/portais de boss — sobrescrevem a
    # regiao maior (ceu_ventos/centro) nas suas proprias celulas, pois entram
    # depois no dict (ultima atribuicao vence no _REGION_LOOKUP).
    "vazio_sombrio": {
        "name": "Vazio Sombrio",
        "color": (150, 60, 200),
        "tiles": [(c, r) for c in range(1, 15) for r in range(1, 6)],
    },
    "bosque_sagrado": {
        "name": "Bosque Sagrado",
        "color": (60, 200, 60),
        "tiles": [(c, r) for c in range(12, 19) for r in range(13, 19)],
    },
}
