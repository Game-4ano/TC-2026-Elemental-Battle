"""
Subpacote de tiles do Elemental Battle.

Reexporta todas as classes de tile para que `core/map.py` faca
`from meu_jogo.core.tiles import *` e imports historicos como
`from meu_jogo.core.map import GrassTile` continuem validos.
"""

from meu_jogo.core.tiles.base import Tile
from meu_jogo.core.tiles.terrain import (
    GrassTile, WallTile, FlowerGrassTile, BushTile, TreeTile,
)
from meu_jogo.core.tiles.water_tiles import (
    WaterTile, IceTile, CrystalTile, RiverTile, WetSandTile,
    DeepWaterTile, IceStalactiteTile, BubbleTile, MushroomTile,
)
from meu_jogo.core.tiles.fire_tiles import (
    FireTile, LavaTile, HotRockTile, AshTile, EmberTile, LavaDropTile, BoneTile,
)
from meu_jogo.core.tiles.wind_tiles import (
    WindTile, CloudTile, SkyPathTile, WindyGrassTile, FeatherTile, SkyVoidTile,
)
from meu_jogo.core.tiles.electric_tiles import (
    SandTile, ChargedSandTile, MetalTile, LightningCrystalTile,
    CircuitFloorTile, NeonBorderTile, BoltTile,
)
from meu_jogo.core.tiles.path_tiles import (
    StoneRoadTile, WoodPathTile, WoodBridgeTile,
)
from meu_jogo.core.tiles.arena_tiles import (
    IceArenaTile, VolcanoFloorTile, SkyArenaTile, MetalArenaTile,
)
from meu_jogo.core.tiles.shadow_tiles import (
    VoidFloorTile, ShadowCrystalTile, DarkMistTile,
)
from meu_jogo.core.tiles.portal import PortalTile

__all__ = [
    "Tile",
    "GrassTile", "WallTile", "FlowerGrassTile", "BushTile", "TreeTile",
    "WaterTile", "IceTile", "CrystalTile", "RiverTile", "WetSandTile",
    "DeepWaterTile", "IceStalactiteTile", "BubbleTile", "MushroomTile",
    "FireTile", "LavaTile", "HotRockTile", "AshTile", "EmberTile", "LavaDropTile",
    "BoneTile",
    "WindTile", "CloudTile", "SkyPathTile", "WindyGrassTile", "FeatherTile",
    "SkyVoidTile",
    "SandTile", "ChargedSandTile", "MetalTile", "LightningCrystalTile",
    "CircuitFloorTile", "NeonBorderTile", "BoltTile",
    "StoneRoadTile", "WoodPathTile", "WoodBridgeTile",
    "IceArenaTile", "VolcanoFloorTile", "SkyArenaTile", "MetalArenaTile",
    "VoidFloorTile", "ShadowCrystalTile", "DarkMistTile",
    "PortalTile",
]
