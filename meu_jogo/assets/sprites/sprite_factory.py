"""
meu_jogo/midia/sprites/sprite_factory.py

Carrega sprites a partir de arquivos PNG no diretorio de sprites.
Fallback: retorna None e o CharacterObject usa retangulo colorido.
"""

import os as _os
import pygame


_SPRITES_DIR = _os.path.join(_os.path.dirname(_os.path.abspath(__file__)))

# ─────────────────────────────────────────────────────────────────────────────
#  Mapeamento sprite_key → arquivo PNG
# ─────────────────────────────────────────────────────────────────────────────

_PNG_MAP = {
    "tide_crawler":    "bossagua.png",
    "magma_titan":     "bossfogo.png",
    "forest_guardian": "bossterra.png",
    "storm_eagle":     "bossvento.png",
    "storm_beast":     "bosseletrico.png",
    "void_emperor":    "ultimatebosstodososelementos.png",
    "slime":           "slimeterra.png",
    "slimeagua":       "slimeagua.png",
    "slimefogo":       "slimefogo.png",
    "slimevento":      "slimevento.png",
}

_HERO_SHEET_FILE = "spritepersonagem.png"
_HERO_SHEET_COLS = 4
_HERO_SHEET_ROWS = 4

_HERO_SHEET_ANIMS = {
    "hero_idle":        [(0, 0)],
    "hero_walk_front":  [(0, 0), (0, 1), (0, 0), (0, 2), (0, 0)],
    "hero_walk":        [(1, 0), (1, 1), (1, 0), (1, 2), (1, 0)],
    "hero_walk_back":   [(2, 0), (2, 1), (2, 0), (2, 2), (2, 0)],
    "hero_idle_breath": [(0, 0), (0, 3)],
    "hero_attack":      [(1, 0), (1, 1)],
    "hero_hurt":        [(0, 0)],
}


# ─────────────────────────────────────────────────────────────────────────────
#  Caches
# ─────────────────────────────────────────────────────────────────────────────

_cache: dict[tuple[str, int], pygame.Surface | None] = {}
_anim_cache: dict[tuple[str, int], list[pygame.Surface]] = {}
_sheet_cell_cache: dict[tuple[int, int, int], pygame.Surface | None] = {}
_scene_cache: dict[tuple[str, int, int], pygame.Surface | None] = {}
_hero_sheet_raw: pygame.Surface | None = None
_hero_sheet_loaded: bool = False


def get_scene_image(filename: str, width: int, height: int) -> pygame.Surface | None:
    """Carrega um PNG de cenario (fundo/mapa) escalado para (width, height).
    Retorna None se o arquivo nao existir ou falhar."""
    cache_key = (filename, width, height)
    if cache_key in _scene_cache:
        return _scene_cache[cache_key]
    path = _os.path.join(_SPRITES_DIR, filename)
    surf = None
    if _os.path.isfile(path):
        try:
            raw = pygame.image.load(path).convert()
            surf = pygame.transform.smoothscale(raw, (width, height))
        except Exception:
            surf = None
    _scene_cache[cache_key] = surf
    return surf


# ─────────────────────────────────────────────────────────────────────────────
#  Carregamento de PNGs
# ─────────────────────────────────────────────────────────────────────────────

def _get_hero_sheet() -> pygame.Surface | None:
    global _hero_sheet_raw, _hero_sheet_loaded
    if _hero_sheet_loaded:
        return _hero_sheet_raw
    _hero_sheet_loaded = True
    path = _os.path.join(_SPRITES_DIR, _HERO_SHEET_FILE)
    if _os.path.isfile(path):
        try:
            _hero_sheet_raw = pygame.image.load(path).convert()
            _hero_sheet_raw.set_colorkey((255, 255, 255))
        except Exception:
            pass
    return _hero_sheet_raw


def _load_png_surface(filename: str, target_size: int) -> pygame.Surface | None:
    path = _os.path.join(_SPRITES_DIR, filename)
    if not _os.path.isfile(path):
        return None
    try:
        raw = pygame.image.load(path)
        img_a = raw.convert_alpha()
        bbox_a = img_a.get_bounding_rect(min_alpha=10)
        img_ck = raw.convert()
        img_ck.set_colorkey((255, 255, 255))
        img_ck = img_ck.convert_alpha()
        bbox_ck = img_ck.get_bounding_rect(min_alpha=10)
        if bbox_ck.width * bbox_ck.height < bbox_a.width * bbox_a.height:
            img, bbox = img_ck, bbox_ck
        else:
            img, bbox = img_a, bbox_a
        if bbox.width == 0 or bbox.height == 0:
            return None
        cropped = img.subsurface(bbox).copy()
        ratio = min(target_size / cropped.get_width(),
                    target_size / cropped.get_height())
        new_w = max(1, int(cropped.get_width() * ratio))
        new_h = max(1, int(cropped.get_height() * ratio))
        scaled = pygame.transform.smoothscale(cropped, (new_w, new_h))
        result = pygame.Surface((target_size, target_size), pygame.SRCALPHA)
        result.blit(scaled, ((target_size - new_w) // 2,
                             (target_size - new_h) // 2))
        return result
    except Exception:
        return None


def _load_sheet_cell(row: int, col: int, target_size: int) -> pygame.Surface | None:
    cache_key = (row, col, target_size)
    if cache_key in _sheet_cell_cache:
        return _sheet_cell_cache[cache_key]
    sheet = _get_hero_sheet()
    if sheet is None:
        _sheet_cell_cache[cache_key] = None
        return None
    try:
        cell_w = sheet.get_width() // _HERO_SHEET_COLS
        cell_h = sheet.get_height() // _HERO_SHEET_ROWS
        x, y = col * cell_w, row * cell_h
        if x + cell_w > sheet.get_width() or y + cell_h > sheet.get_height():
            _sheet_cell_cache[cache_key] = None
            return None
        cell = sheet.subsurface(pygame.Rect(x, y, cell_w, cell_h)).copy()
        cell = cell.convert()
        cell.set_colorkey((255, 255, 255))
        if cell.get_width() == 0 or cell.get_height() == 0:
            _sheet_cell_cache[cache_key] = None
            return None
        result = pygame.transform.scale(cell, (target_size, target_size))
        result.set_colorkey((255, 255, 255))
        _sheet_cell_cache[cache_key] = result
        return result
    except Exception:
        _sheet_cell_cache[cache_key] = None
        return None


# ─────────────────────────────────────────────────────────────────────────────
#  API publica
# ─────────────────────────────────────────────────────────────────────────────

def get_sprite(sprite_key: str, scale: int = 4) -> pygame.Surface | None:
    """Retorna Surface do sprite PNG, ou None se nao existir."""
    cache_key = (sprite_key, scale)
    if cache_key in _cache:
        return _cache[cache_key]
    target = 16 * scale
    surf = None
    if sprite_key in _PNG_MAP:
        surf = _load_png_surface(_PNG_MAP[sprite_key], target)
    elif sprite_key == "hero":
        surf = _load_sheet_cell(0, 0, target)
    _cache[cache_key] = surf
    return surf


def get_animation(anim_key: str, scale: int = 4) -> list[pygame.Surface]:
    """Retorna lista de frames para animacao, ou lista vazia."""
    cache_key = (anim_key, scale)
    if cache_key in _anim_cache:
        return _anim_cache[cache_key]
    target = 16 * scale
    frames: list[pygame.Surface] = []

    if anim_key in _HERO_SHEET_ANIMS:
        for row, col in _HERO_SHEET_ANIMS[anim_key]:
            f = _load_sheet_cell(row, col, target)
            if f is None:
                return []
            frames.append(f)
    else:
        for skey in _PNG_MAP:
            for suffix in ("_idle", "_attack", "_hurt", "_death"):
                if anim_key == skey + suffix:
                    base = get_sprite(skey, scale)
                    if base is None:
                        return []
                    if suffix == "_idle":
                        shifted = pygame.Surface(base.get_size(), pygame.SRCALPHA)
                        shifted.blit(base, (0, -1))
                        frames = [base, shifted]
                    else:
                        frames = [base]
                    break
            if frames:
                break

    if frames:
        _anim_cache[cache_key] = frames
    return frames


def list_sprites() -> list[str]:
    return list(_PNG_MAP.keys()) + ["hero"]


def list_animations() -> list[str]:
    result = list(_HERO_SHEET_ANIMS.keys())
    for skey in _PNG_MAP:
        for suffix in ("_idle", "_attack", "_hurt", "_death"):
            result.append(skey + suffix)
    return result
