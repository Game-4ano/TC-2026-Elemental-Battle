"""
meu_jogo/midia/sprites/sprite_factory.py

Gera sprites de pixel art (pygame.Surface) programaticamente.
Nenhum arquivo de imagem externo é necessário.

USO:
    from meu_jogo.midia.sprites.sprite_factory import get_sprite

    surface = get_sprite("slime", scale=4)   # 16x16 escalado 4x = 64x64
    surface = get_sprite("hero",  scale=4)

CONVENÇÃO DE CARACTERES NAS MATRIZES:
    '.' → transparente
    Qualquer outra letra → índice na paleta de cores do personagem

Cada personagem tem:
    - PIXELS  : lista de strings (matriz do sprite 16x16)
    - PALETTE : dict  letra → (R, G, B)  ou  (R, G, B, A)
"""

import pygame


# ─────────────────────────────────────────────────────────────────────────────
#  UTILITÁRIOS
# ─────────────────────────────────────────────────────────────────────────────

def _build_surface(pixels: list[str], palette: dict, scale: int = 4) -> pygame.Surface:
    """
    Constrói uma pygame.Surface a partir de uma matriz de pixels e uma paleta.
    Se scale > 1, aplica pygame.transform.scale para o efeito pixel art "gordinho".
    """
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
#  HERÓI  (elemento: Fogo)
# ─────────────────────────────────────────────────────────────────────────────

_HERO_PALETTE = {
    'S': (220, 180, 130),  # pele
    'H': ( 60,  40, 120),  # roupa (azul escuro)
    'h': ( 90,  70, 160),  # roupa clara
    'B': ( 40,  25,  80),  # contorno roupa
    'C': (200, 100,  30),  # cabelo laranja (fogo)
    'c': (240, 150,  50),  # cabelo claro
    'E': ( 30,  30,  30),  # olhos / contorno
    'W': (255, 255, 255),  # branco dos olhos
    'b': ( 80,  50,  20),  # bota
    'G': (200,  60,  40),  # detalhe vermelho (emblema fogo)
    'g': (240, 120,  60),  # detalhe laranja claro
}

_HERO_PIXELS = [
    "....cCCCCc....",   # 00
    "...cCCCCCCc...",   # 01
    "...CCCCCCC....",   # 02
    "...SSSSSSS....",   # 03  cabeça
    "..ESSWSWSE...",    # 04  olhos
    "...SSSSSSS....",   # 05
    "...SEEEEEES...",   # 06  boca
    "..BHHGGHHHB..",    # 07  ombros/tronco
    "..BhhhGGhhHB.",    # 08
    "..BHHhhhHHHB.",    # 09
    "..BHH...HHHB.",    # 10  cintura
    "...HH...HHH..",    # 11
    "..bHH...HHbb.",    # 12  pernas
    "..bHH...HHbb.",    # 13
    "..bbb...bbbb.",    # 14  botas
    "..bbb...bbbb.",    # 15
]

# ─────────────────────────────────────────────────────────────────────────────
#  SLIME  (elemento: Água/Grama)
# ─────────────────────────────────────────────────────────────────────────────

_SLIME_PALETTE = {
    'G': ( 60, 200,  80),  # verde corpo
    'g': (100, 230, 110),  # verde claro (brilho)
    'd': ( 30, 120,  50),  # verde escuro (sombra)
    'W': (255, 255, 255),  # branco olho
    'E': ( 20,  20,  20),  # pupila
    'B': ( 20,  80,  30),  # contorno
    'H': (180, 255, 180),  # reflexo topo
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
    ".BddddgggggddddB",  # 10
    "..BdddgggggdddB.",
    "...BBdddddddBB..",
    ".....BBBBBBB....",
    "................",
    "................",
]

# ─────────────────────────────────────────────────────────────────────────────
#  EMBER SPRITE  (elemento: Fogo)
# ─────────────────────────────────────────────────────────────────────────────

_EMBER_PALETTE = {
    'R': (220,  60,  20),  # vermelho fogo
    'r': (255, 120,  40),  # laranja claro
    'Y': (255, 220,  60),  # amarelo centro
    'y': (255, 240, 140),  # amarelo brilho
    'E': ( 20,  20,  20),  # olhos
    'W': (255, 255, 255),
    'B': (120,  20,   0),  # contorno escuro
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
#  LEAF WISP  (elemento: Grama)
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
#  GOBLIN  (elemento: Grama, médio)
# ─────────────────────────────────────────────────────────────────────────────

_GOBLIN_PALETTE = {
    'S': ( 90, 160,  60),  # pele verde
    's': (120, 190,  80),  # pele clara
    'E': ( 20,  20,  20),
    'W': (255, 255, 255),
    'R': (200,  40,  40),  # roupa vermelha
    'r': (160,  30,  30),
    'B': ( 30,  70,  20),  # contorno
    'T': (180, 140,  60),  # presas/dentes
    'b': ( 50,  30,  10),  # bota
    'H': ( 60,  40,  10),  # cabelo
}

_GOBLIN_PIXELS = [
    ".....BSSSSB.....",
    "....BSssssSB....",
    "...BSssssssSB...",
    "..BSssEsssEssB..",
    "..BSssWsssWssB..",
    "..BSssssssssssB.",
    "...BTTssssTTB...",  # presas
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
#  FLAME HOUND  (elemento: Fogo, médio)
# ─────────────────────────────────────────────────────────────────────────────

_FLAME_HOUND_PALETTE = {
    'D': (180,  60,  10),  # corpo laranja escuro
    'd': (220,  90,  30),  # corpo laranja
    'O': (255, 140,  40),  # laranja claro
    'Y': (255, 220,  60),  # amarelo (chamas)
    'y': (255, 240, 130),
    'E': ( 20,  20,  20),
    'N': (100,  30,   5),  # focinho escuro
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
#  WOLF  (elemento: Grama, forte)
# ─────────────────────────────────────────────────────────────────────────────

_WOLF_PALETTE = {
    'W': (190, 190, 200),  # pelo cinza claro
    'w': (140, 140, 155),  # pelo cinza médio
    'D': ( 70,  70,  85),  # pelo escuro
    'd': ( 40,  40,  55),
    'E': ( 20,  20,  20),
    'N': ( 50,  30,  30),  # focinho
    'T': (230, 230, 240),  # barriga
    'G': ( 60, 180,  60),  # olhos verdes (elemento grama)
    'B': ( 20,  20,  30),
    'R': (200,  30,  30),  # língua
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
#  FOREST GUARDIAN  (boss, elemento: Grama)
# ─────────────────────────────────────────────────────────────────────────────

_GUARDIAN_PALETTE = {
    'G': ( 30, 120,  40),  # verde escuro madeira
    'g': ( 50, 160,  60),
    'L': ( 80, 200,  80),  # folhas
    'l': (130, 230, 110),
    'y': (200, 220,  50),  # brilho mágico
    'Y': (240, 255, 100),
    'B': ( 15,  60,  20),  # contorno
    'E': (200, 255,  50),  # olhos brilhantes
    'e': (100, 200,  30),
    'W': (220, 240, 180),  # face/tronco claro
    'R': (180,  50,  30),  # runas (detalhes vermelhos)
    'r': (220,  80,  50),
    'T': (120,  80,  40),  # tronco/madeira
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
#  VOID EMPEROR  (boss final, elemento: Dark)
# ─────────────────────────────────────────────────────────────────────────────

_VOID_PALETTE = {
    'P': ( 50,  20,  80),  # roxo escuro corpo
    'p': ( 80,  40, 120),  # roxo médio
    'V': (120,  60, 180),  # violeta
    'v': (180, 100, 240),  # violeta claro
    'E': (200, 150, 255),  # olhos roxo brilhante
    'e': (240, 200, 255),
    'B': ( 15,   5,  30),  # contorno muito escuro
    'Y': (220, 180, 255),  # brilho aura
    'y': (255, 220, 255),
    'R': (180,  20, 200),  # runas magenta
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
#  STORM RAVEN  (elemento: Elétrico, médio)
# ─────────────────────────────────────────────────────────────────────────────

_RAVEN_PALETTE = {
    'D': ( 30,  30,  40),  # preto azulado
    'd': ( 50,  50,  70),
    'B': ( 10,  10,  20),
    'Y': (220, 200,  30),  # amarelo elétrico
    'y': (255, 240, 100),
    'E': (255, 240,  50),  # olhos elétricos
    'W': (200, 200, 220),  # penas brancas
    'w': (160, 160, 190),
    'G': ( 80,  80, 100),
}

_RAVEN_PIXELS = [
    "....yYYYYYy.....",
    "...yYyyyy Yy....",
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
#  TIDE CRAWLER  (elemento: Água, médio)
# ─────────────────────────────────────────────────────────────────────────────

_TIDE_PALETTE = {
    'B': ( 20,  60, 140),  # azul escuro
    'b': ( 40,  90, 180),
    'C': ( 60, 140, 220),  # azul claro
    'c': (100, 180, 240),
    'T': (180, 230, 255),  # brilho água
    'E': (200, 240, 255),  # olhos
    'e': ( 10,  30,  80),  # pupila
    'G': ( 30, 200, 160),  # verde água
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
#  REGISTRO  –  sprite_key → (pixels, palette)
# ─────────────────────────────────────────────────────────────────────────────

_SPRITE_DATA: dict[str, tuple[list[str], dict]] = {
    "hero":           (_HERO_PIXELS,        _HERO_PALETTE),
    "slime":          (_SLIME_PIXELS,       _SLIME_PALETTE),
    "ember_sprite":   (_EMBER_PIXELS,       _EMBER_PALETTE),
    "leaf_wisp":      (_LEAF_PIXELS,        _LEAF_PALETTE),
    "goblin":         (_GOBLIN_PIXELS,      _GOBLIN_PALETTE),
    "flame_hound":    (_FLAME_HOUND_PIXELS, _FLAME_HOUND_PALETTE),
    "storm_raven":    (_RAVEN_PIXELS,       _RAVEN_PALETTE),
    "tide_crawler":   (_TIDE_PIXELS,        _TIDE_PALETTE),
    "wolf":           (_WOLF_PIXELS,        _WOLF_PALETTE),
    "forest_guardian":(_GUARDIAN_PIXELS,    _GUARDIAN_PALETTE),
    "void_emperor":   (_VOID_PIXELS,        _VOID_PALETTE),
}

# Cache para não recriar surfaces desnecessariamente
_cache: dict[tuple[str, int], pygame.Surface] = {}


def get_sprite(sprite_key: str, scale: int = 4) -> pygame.Surface | None:
    """
    Retorna a pygame.Surface do sprite escalada.

    Args:
        sprite_key : chave do personagem (ex: "slime", "hero")
        scale      : fator de escala — 4 transforma 16x16 em 64x64

    Returns:
        pygame.Surface com transparência, ou None se a chave não existir.
    """
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


def list_sprites() -> list[str]:
    """Retorna lista de todas as chaves de sprites disponíveis."""
    return list(_SPRITE_DATA.keys())