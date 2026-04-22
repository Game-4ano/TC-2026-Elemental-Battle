"""
meu_jogo/midia/sprites/sprite_factory.py

Gera sprites de pixel art (pygame.Surface) programaticamente.
Nenhum arquivo de imagem externo é necessário.

USO:
    from meu_jogo.midia.sprites.sprite_factory import get_sprite, get_animation

    # Sprite estático
    surface = get_sprite("slime", scale=4)

    # Lista de frames para animação
    frames = get_animation("hero_walk", scale=4)

CONVENÇÃO DE CARACTERES NAS MATRIZES:
    '.' → transparente
    Qualquer outra letra → índice na paleta de cores do personagem
"""

import pygame


# ─────────────────────────────────────────────────────────────────────────────
#  UTILITÁRIOS
# ─────────────────────────────────────────────────────────────────────────────

import random as _random


def _make_breathing_anim(pixels: list[str], palette: dict) -> list[tuple]:
    """Gera 2 frames de respiração: normal + sprite deslocado 1px para cima."""
    blank = "." * max(len(r) for r in pixels)
    frame_b = list(pixels[1:]) + [blank]
    return [(pixels, palette), (frame_b, palette)]


def _make_death_frames(pixels: list[str], palette: dict) -> list[tuple]:
    """Gera 3 frames de morte por dissolução progressiva (seed determinística)."""
    rng = _random.Random(sum(ord(c) for c in pixels[0]))

    def dissolve(rows: list[str], keep: float) -> list[str]:
        return [
            ''.join(c if c == '.' or rng.random() < keep else '.' for c in row)
            for row in rows
        ]

    return [
        (pixels,             palette),
        (dissolve(pixels, 0.55), palette),
        (dissolve(pixels, 0.20), palette),
    ]


def _build_surface(pixels: list[str], palette: dict, scale: int = 4) -> pygame.Surface:
    h = len(pixels)
    w = max(len(row) for row in pixels)
    surf = pygame.Surface((w, h), pygame.SRCALPHA)
    surf.fill((0, 0, 0, 0))
    for y, row in enumerate(pixels):
        for x, ch in enumerate(row):
            if ch == '.':
                continue
            color = palette.get(ch)
            if color:
                surf.set_at((x, y), color)
    if scale > 1:
        surf = pygame.transform.scale(surf, (w * scale, h * scale))
    return surf


# ─────────────────────────────────────────────────────────────────────────────
#  PALETA COMPARTILHADA DO HERÓI
# ─────────────────────────────────────────────────────────────────────────────

_HERO_PALETTE = {
    'S': (220, 180, 130),  # pele
    'H': ( 60,  40, 120),  # roupa azul escuro
    'h': ( 90,  70, 160),  # roupa azul claro
    'B': ( 40,  25,  80),  # contorno roupa
    'C': (200, 100,  30),  # cabelo laranja
    'c': (240, 150,  50),  # cabelo claro
    'E': ( 30,  30,  30),  # olhos / contorno
    'W': (255, 255, 255),  # branco dos olhos
    'b': ( 80,  50,  20),  # bota
    'G': (200,  60,  40),  # emblema fogo
    'g': (240, 120,  60),  # emblema laranja claro
}

# ─────────────────────────────────────────────────────────────────────────────
#  HERÓI — frame IDLE (parado)
# ─────────────────────────────────────────────────────────────────────────────

_HERO_IDLE = [
    "....cCCCCc....",
    "...cCCCCCCc...",
    "...CCCCCCC....",
    "...SSSSSSS....",
    "..ESSWSWSE...",
    "...SSSSSSS....",
    "...SEEEEEES...",
    "..BHHGGHHHB..",
    "..BhhhGGhhHB.",
    "..BHHhhhHHHB.",
    "..BHH...HHHB.",
    "...HH...HHH..",
    "..bHH...HHbb.",
    "..bHH...HHbb.",
    "..bbb...bbbb.",
    "..bbb...bbbb.",
]

# ─────────────────────────────────────────────────────────────────────────────
#  HERÓI — frame WALK-A (perna esquerda à frente)
# ─────────────────────────────────────────────────────────────────────────────

_HERO_WALK_A = [
    "....cCCCCc....",
    "...cCCCCCCc...",
    "...CCCCCCC....",
    "...SSSSSSS....",
    "..ESSWSWSE...",
    "...SSSSSSS....",
    "...SEEEEEES...",
    "..BHHGGHHHB..",
    "..BhhhGGhhHB.",
    "..BHHhhhHHHB.",
    "..BHH...HHHB.",
    "...HH...HHH..",
    "..bHHb..HH...",   # perna esq à frente, dir atrás
    "..bHHbb.HH...",
    "..bbbb..HHb..",
    ".......bbbbb.",
]

# ─────────────────────────────────────────────────────────────────────────────
#  HERÓI — frame WALK-B (perna direita à frente)
# ─────────────────────────────────────────────────────────────────────────────

_HERO_WALK_B = [
    "....cCCCCc....",
    "...cCCCCCCc...",
    "...CCCCCCC....",
    "...SSSSSSS....",
    "..ESSWSWSE...",
    "...SSSSSSS....",
    "...SEEEEEES...",
    "..BHHGGHHHB..",
    "..BhhhGGhhHB.",
    "..BHHhhhHHHB.",
    "..BHH...HHHB.",
    "...HH...HHH..",
    "...HH..bHHb..",   # perna dir à frente, esq atrás
    "...HH.bbHHbb.",
    "..bHH..bbbb..",
    ".bbbbb.......",
]

# ─────────────────────────────────────────────────────────────────────────────
#  HERÓI — frame WALK-C (levemente agachado, transição)
# ─────────────────────────────────────────────────────────────────────────────

_HERO_WALK_C = [
    ".....cCCCCc...",
    "....cCCCCCCc..",
    "....CCCCCCC...",
    "....SSSSSSS...",
    "...ESSWSWSE..",
    "....SSSSSSS...",
    "....SEEEEEES.",
    "...BHHGGHHHB.",
    "...BhhhGGhhHB",
    "...BHHhhhHHHB",
    "...BHH...HHHB",
    "....HH...HHH.",
    "...bHH...HHbb",   # pernas levemente abertas
    "..bbHH...HHbb",
    "..bbb.....bbb",
    "..bbb.....bbb",
]

# ─────────────────────────────────────────────────────────────────────────────
#  SLIME
# ─────────────────────────────────────────────────────────────────────────────

_SLIME_PALETTE = {
    'G': ( 60, 200,  80),
    'g': (100, 230, 110),
    'd': ( 30, 120,  50),
    'W': (255, 255, 255),
    'E': ( 20,  20,  20),
    'B': ( 20,  80,  30),
    'H': (180, 255, 180),
}

_SLIME_PIXELS = [
    "......BBBB......",
    "....BBgggGBB....",
    "...BgHHgggGGB...",
    "..BgHHggggGGGB..",
    ".BggggggggggggB.",
    "BGggggWWEWWgggGB",
    "BGgggWEEEEWggggB",
    "BGgggWEEEEWggggB",
    "BGgggggggggggggB",
    "BGdddgggggggdddB",
    ".BddddgggggddddB",
    "..BdddgggggdddB.",
    "...BBdddddddBB..",
    ".....BBBBBBB....",
    "................",
    "................",
]

# ─────────────────────────────────────────────────────────────────────────────
#  EMBER SPRITE  (Fogo)
# ─────────────────────────────────────────────────────────────────────────────

_EMBER_PALETTE = {
    'R': (220,  60,  20),
    'r': (255, 120,  40),
    'Y': (255, 220,  60),
    'y': (255, 240, 140),
    'E': ( 20,  20,  20),
    'W': (255, 255, 255),
    'B': (120,  20,   0),
    'k': ( 40,  10,   0),
}

_EMBER_PIXELS = [
    "......yrY.......",
    ".....yYYYr......",
    "....rYYYYYr.....",
    "...rRYYYYYRr....",
    "..BRRrYYYrRRB...",
    ".BRRRrWEWrRRRB..",
    "BRRRRrWEWrRRRRB.",
    "BRRRRRrrrRRRRRB.",
    "BRRRRRRRRRRRrRB.",
    ".BRRRRRRRRRRrB..",
    "..BRrRRRRRrRB...",
    "...BRrrrrrRB....",
    "....BBrRrBB.....",
    ".....BRRB.......",
    "......BB........",
    "................",
]

# ─────────────────────────────────────────────────────────────────────────────
#  LEAF WISP  (Grama)
# ─────────────────────────────────────────────────────────────────────────────

_LEAF_PALETTE = {
    'G': ( 50, 180,  60),
    'g': (100, 220, 100),
    'L': ( 30, 130,  40),
    'l': ( 20,  80,  30),
    'Y': (180, 220,  50),
    'y': (220, 255,  80),
    'E': ( 10,  40,  10),
    'W': (230, 255, 200),
    'B': ( 10,  50,  10),
}

_LEAF_PIXELS = [
    "....yYYYYYy.....",
    "...yYyyyYYYy....",
    "..GgyyyyyYYGg...",
    ".GGgyyyyyyyyGGg.",
    "GGGgyyWEWyygGGG.",
    "GGGggyyEEyyggGGG",
    "GGGggyyyyyygGGGG",
    ".GGggggggggggGG.",
    "..LGGGggggGGGL..",
    "...LLGGggGGLL...",
    "....lLGGGGLl....",
    ".....lLGGLl.....",
    "......lGGl......",
    ".......ll.......",
    "................",
    "................",
]

# ─────────────────────────────────────────────────────────────────────────────
#  GOBLIN  (Grama, médio)
# ─────────────────────────────────────────────────────────────────────────────

_GOBLIN_PALETTE = {
    'S': ( 90, 160,  60),
    's': (120, 190,  80),
    'E': ( 20,  20,  20),
    'W': (255, 255, 255),
    'R': (200,  40,  40),
    'r': (160,  30,  30),
    'B': ( 30,  70,  20),
    'T': (180, 140,  60),
    'b': ( 50,  30,  10),
    'H': ( 60,  40,  10),
}

_GOBLIN_PIXELS = [
    ".....BSSSSB.....",
    "....BSssssSB....",
    "...BSssssssSB...",
    "..BSssEsssEssB..",
    "..BSssWsssWssB..",
    "..BSssssssssssB.",
    "...BTTssssTTB...",
    "....BRRRRRRB....",
    "...BRRrRRrRRB...",
    "...BRRRRRRRrB...",
    "....BRR.RRRB....",
    "....BRR.RRRB....",
    "....brr.rrrb....",
    "....brr.rrrb....",
    "....bbb.bbbb....",
    "................",
]

# ─────────────────────────────────────────────────────────────────────────────
#  FLAME HOUND  (Fogo, médio)
# ─────────────────────────────────────────────────────────────────────────────

_FLAME_HOUND_PALETTE = {
    'D': (180,  60,  10),
    'd': (220,  90,  30),
    'O': (255, 140,  40),
    'Y': (255, 220,  60),
    'y': (255, 240, 130),
    'E': ( 20,  20,  20),
    'N': (100,  30,   5),
    'B': ( 80,  20,   0),
    'W': (255, 255, 255),
    'K': ( 20,  10,   0),
}

_FLAME_HOUND_PIXELS = [
    "..YyY...........",
    ".yYYYy.....YyY..",
    "yYYYYYy...yYYYy.",
    ".yYYYy.....yYy..",
    "..BDDDDDDDDDDb..",
    ".BDDdOOOOOOdDDB.",
    "BDDdOOWEOWEOdDDB",
    "BDDdOOONNNOOdDDB",
    "BDdOOONNNNNOOdDB",
    ".BDdOOOOOOOOdDB.",
    "..BDDDDDDDDDDDB.",
    ".BD.DD...DD.DDB.",
    ".BD.DD...DD.DDB.",
    ".BD.BB...BB.BDB.",
    "..B..B...B..B...",
    "................",
]

# ─────────────────────────────────────────────────────────────────────────────
#  STORM RAVEN  (Elétrico, médio)
# ─────────────────────────────────────────────────────────────────────────────

_RAVEN_PALETTE = {
    'D': ( 30,  30,  40),
    'd': ( 50,  50,  70),
    'B': ( 10,  10,  20),
    'Y': (220, 200,  30),
    'y': (255, 240, 100),
    'E': (255, 240,  50),
    'W': (200, 200, 220),
    'w': (160, 160, 190),
    'G': ( 80,  80, 100),
}

_RAVEN_PIXELS = [
    "....yYYYYYy.....",
    "...yYyyyyYYy....",
    "..DDDDddddDDD...",
    ".DDDdGGGGGdDDD..",
    "DDDdGGEEEGGdDDD.",
    "DDdGGEEEEEGGdDDD",
    "DDdGGGEEEGGGdDDD",
    "DDDdGGGGGGGdDDD.",
    ".DDDdddddddDDD..",
    "..WDDDDDDDDDw...",
    ".WwDDDyYydDDwW..",
    "WwwDDDyYyDDDwwW.",
    ".WwwDDDDDDDwwW..",
    "..WwwDDD.DwwW...",
    "....WwD...WwW...",
    ".....W.....W....",
]

# ─────────────────────────────────────────────────────────────────────────────
#  TIDE CRAWLER  (Água, médio)
# ─────────────────────────────────────────────────────────────────────────────

_TIDE_PALETTE = {
    'B': ( 20,  60, 140),
    'b': ( 40,  90, 180),
    'C': ( 60, 140, 220),
    'c': (100, 180, 240),
    'T': (180, 230, 255),
    'E': (200, 240, 255),
    'e': ( 10,  30,  80),
    'G': ( 30, 200, 160),
    'g': ( 60, 230, 190),
    'K': ( 10,  20,  50),
}

_TIDE_PIXELS = [
    "....KBBBBBBk....",
    "...KBbCCCCbBK...",
    "..KBbCcccccBbK..",
    ".KBbCcTEeTcCbBK.",
    "KBbCcTEeeeETcCbK",
    "KBbCcTEeeeETcCbK",
    "KBbCcCcccccCcCbK",
    "KBbCGCcccccCGCbK",
    "KBbCGgCcccCgGCbK",
    ".KBbCGgggggGCbK.",
    "..KBbCGgGgGCbK..",
    "...KBbK...KbBK..",
    "...KBK.....KBK..",
    "...BK.......KB..",
    "..KK.........KK.",
    "................",
]

# ─────────────────────────────────────────────────────────────────────────────
#  WOLF  (Grama, forte)
# ─────────────────────────────────────────────────────────────────────────────

_WOLF_PALETTE = {
    'W': (190, 190, 200),
    'w': (140, 140, 155),
    'D': ( 70,  70,  85),
    'd': ( 40,  40,  55),
    'E': ( 20,  20,  20),
    'N': ( 50,  30,  30),
    'T': (230, 230, 240),
    'G': ( 60, 180,  60),
    'B': ( 20,  20,  30),
    'R': (200,  30,  30),
}

_WOLF_PIXELS = [
    "D......D........",
    "dD....dD........",
    "dDWWWWdDWWWW....",
    ".DWWWWDDWwwWD...",
    ".DWWwwwwwwwWD...",
    ".DWwGEwwGEwwD...",
    ".DWwwwwwwwwwD...",
    ".DWwwNNNwwwwD...",
    ".DWwwNRNwwwwD...",
    ".DDWwwwwwwwDD...",
    "..DDWWWWWWDD....",
    "..DWD....DWD....",
    "..DWD....DWD....",
    "..DdD....DdD....",
    "..dBd....dBd....",
    "................",
]

# ─────────────────────────────────────────────────────────────────────────────
#  FOREST GUARDIAN  (boss, Grama)
# ─────────────────────────────────────────────────────────────────────────────

_GUARDIAN_PALETTE = {
    'G': ( 30, 120,  40),
    'g': ( 50, 160,  60),
    'L': ( 80, 200,  80),
    'l': (130, 230, 110),
    'y': (200, 220,  50),
    'Y': (240, 255, 100),
    'B': ( 15,  60,  20),
    'E': (200, 255,  50),
    'e': (100, 200,  30),
    'W': (220, 240, 180),
    'R': (180,  50,  30),
    'r': (220,  80,  50),
    'T': (120,  80,  40),
    't': (160, 110,  60),
}

_GUARDIAN_PIXELS = [
    ".lLlYYYYlLl.....",
    "lLLlYyyYlLLl....",
    "LlLLYyyyYLLlL...",
    ".LLLLYYYYLLLLL..",
    "..BGGGGGGGGGb...",
    ".BGGgWWEEWWgGB..",
    "BGGgWWEEEEWWgGGB",
    "BGGgWWEEEEWWgGGB",
    "BGGGWWRrRrWWGGGB",
    "BGGGGWWrRWWGGGGB",
    ".BGGGTTttTTGGGB.",
    ".BGTTTttttTTTGB.",
    "BTTTt......tTTTB",
    "BTTt........tTTB",
    "BTt..........tTB",
    ".B............B.",
]

# ─────────────────────────────────────────────────────────────────────────────
#  VOID EMPEROR  (boss final, Dark)
# ─────────────────────────────────────────────────────────────────────────────

_VOID_PALETTE = {
    'P': ( 50,  20,  80),
    'p': ( 80,  40, 120),
    'V': (120,  60, 180),
    'v': (180, 100, 240),
    'E': (200, 150, 255),
    'e': (240, 200, 255),
    'B': ( 15,   5,  30),
    'Y': (220, 180, 255),
    'y': (255, 220, 255),
    'R': (180,  20, 200),
    'r': (220,  60, 240),
    'W': (240, 220, 255),
    'K': ( 10,   0,  20),
}

_VOID_PIXELS = [
    ".yYvVVVVvYy.....",
    "yYvVpPPPpVvYy...",
    "YvVpPPPPPpVvY...",
    ".vVpPPEEPPpVv...",
    ".BPPpeEEEepPPB..",
    "BPPppeeeeeepPPB.",
    "BPPpppRrRrpppPPB",
    "BPPppRrrrRrppPPB",
    "BPPpppppppppPPPB",
    ".BPPPVVpppVVPPB.",
    "..BPPPVVVVVPPpB.",
    "..BPPp.....pPPB.",
    ".BVPPp.....pPPVB",
    "BVVPp.......pPVVB",
    ".BVp.........pVB",
    "..B...........B.",
]


# ─────────────────────────────────────────────────────────────────────────────
#  REGISTRO — sprite_key → (pixels, palette)
# ─────────────────────────────────────────────────────────────────────────────

_SPRITE_DATA: dict[str, tuple[list[str], dict]] = {
    "hero":            (_HERO_IDLE,         _HERO_PALETTE),
    "slime":           (_SLIME_PIXELS,      _SLIME_PALETTE),
    "ember_sprite":    (_EMBER_PIXELS,      _EMBER_PALETTE),
    "leaf_wisp":       (_LEAF_PIXELS,       _LEAF_PALETTE),
    "goblin":          (_GOBLIN_PIXELS,     _GOBLIN_PALETTE),
    "flame_hound":     (_FLAME_HOUND_PIXELS,_FLAME_HOUND_PALETTE),
    "storm_raven":     (_RAVEN_PIXELS,      _RAVEN_PALETTE),
    "tide_crawler":    (_TIDE_PIXELS,       _TIDE_PALETTE),
    "wolf":            (_WOLF_PIXELS,       _WOLF_PALETTE),
    "forest_guardian": (_GUARDIAN_PIXELS,   _GUARDIAN_PALETTE),
    "void_emperor":    (_VOID_PIXELS,       _VOID_PALETTE),
}

# Animações: chave → lista ordenada de (pixels, palette)
# O AnimatedSprite vai ciclar por esses frames automaticamente.
_ANIMATION_DATA: dict[str, list[tuple[list[str], dict]]] = {
    # 4 frames: idle → passo-A → idle → passo-B
    "hero_walk": [
        (_HERO_IDLE,   _HERO_PALETTE),
        (_HERO_WALK_A, _HERO_PALETTE),
        (_HERO_WALK_C, _HERO_PALETTE),   # transição agachado
        (_HERO_WALK_B, _HERO_PALETTE),
        (_HERO_WALK_C, _HERO_PALETTE),   # transição agachado
    ],
    "hero_idle": [
        (_HERO_IDLE, _HERO_PALETTE),
    ],
}

# Cache sprites estáticos
_cache: dict[tuple[str, int], pygame.Surface] = {}
# Cache animações (lista de surfaces já escaladas)
_anim_cache: dict[tuple[str, int], list[pygame.Surface]] = {}


def get_sprite(sprite_key: str, scale: int = 4) -> pygame.Surface | None:
    """Retorna a Surface estática do sprite, ou None se a chave não existir."""
    cache_key = (sprite_key, scale)
    if cache_key in _cache:
        return _cache[cache_key]
    data = _SPRITE_DATA.get(sprite_key)
    if data is None:
        return None
    pixels, palette = data
    surf = _build_surface(pixels, palette, scale)
    _cache[cache_key] = surf
    return surf


def get_animation(anim_key: str, scale: int = 4) -> list[pygame.Surface]:
    """
    Retorna a lista de Surfaces que compõem uma animação.
    Retorna lista vazia se a chave não existir.
    """
    cache_key = (anim_key, scale)
    if cache_key in _anim_cache:
        return _anim_cache[cache_key]
    frames_data = _ANIMATION_DATA.get(anim_key)
    if not frames_data:
        return []
    frames = [_build_surface(px, pal, scale) for px, pal in frames_data]
    _anim_cache[cache_key] = frames
    return frames


def list_sprites() -> list[str]:
    return list(_SPRITE_DATA.keys())


def list_animations() -> list[str]:
    return list(_ANIMATION_DATA.keys())