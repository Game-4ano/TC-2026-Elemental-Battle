import pygame

from meu_jogo.core.config import (
    XP_PER_LEVEL,
    HP_LEVEL_INCREMENT,
    DAMAGE_LEVEL_INCREMENT,
    DEFENSE_LEVEL_INCREMENT,
)

class Entity:

    def __init__(
        self,
        hp: int,
        damage: int,
        defense: int,
        magic: int = 0,
        x: float = 0.0,
        y: float = 0.0,
    ):
        self.max_hp   = hp
        self.hp       = float(hp)
        self.damage   = damage
        self.defense  = defense
        self.magic    = magic

        self.position = pygame.Vector2(x, y)
        self.velocity = pygame.Vector2(0.0, 0.0)

        self.is_defending = False

    def move(self, dt: float):
        self.position += self.velocity * dt


    def take_damage(self, amount: int) -> int:
        
        if self.is_defending:
            real = max(amount - self.defense, 0)
            self.is_defending = False
        else:
            real = max(amount - self.defense // 2, 0)

        self.hp = max(self.hp - real, 0.0)
        return real

    def attack(self, target: "Entity", damage_calculator) -> int:
        raw = damage_calculator(self, target)
        return target.take_damage(raw)

    def heal(self, amount: int):
        self.hp = min(self.hp + amount, float(self.max_hp))

    def defend(self):
        self.is_defending = True

    def is_alive(self) -> bool:
        return self.hp > 0


class Character(Entity):
    
    def __init__(
        self,
        name: str,
        hp: int,
        damage: int,
        defense: int,
        element: str,
        weakness: str,
        magic: int = 0,
        is_boss: bool = False,
        sprite_key: str | None = None,
        x: float = 0.0,
        y: float = 0.0,
    ):
        super().__init__(hp=hp, damage=damage, defense=defense, magic=magic, x=x, y=y)

        self.name       = name
        self.element    = element
        self.weakness   = weakness
        self.is_boss    = is_boss
        self.sprite_key = sprite_key

        self.level = 1
        self.xp    = 0

        self.on_level_up = None  


    def gain_xp(self, amount: int):
        self.xp += amount
        while self.xp >= XP_PER_LEVEL:
            self.xp -= XP_PER_LEVEL
            self.level_up()

    def level_up(self):
        self.level   += 1
        self.max_hp  += HP_LEVEL_INCREMENT
        self.damage  += DAMAGE_LEVEL_INCREMENT
        self.defense += DEFENSE_LEVEL_INCREMENT
        self.hp       = float(self.max_hp)
        if self.on_level_up:
            self.on_level_up(self)


# slime = Character(
#     name="Slime",
#     hp=50, damage=10, defense=2, magic=0,
#     element="Grass", weakness="Fire",
#     sprite_key="slime",
# )

# goblin = Character(
#     name="Goblin",
#     hp=70, damage=12, defense=4, magic=5,
#     element="Grass", weakness="Fire",
#     sprite_key="goblin",
# )

# wolf = Character(
#     name="Wolf",
#     hp=60, damage=15, defense=3, magic=0,
#     element="Grass", weakness="Fire",
#     sprite_key="wolf",
# )

forest_guardian = Character(
    name="Forest Guardian",
    hp=150, damage=25, defense=8, magic=20,
    element="Grass", weakness="Fire",
    is_boss=True,
    sprite_key="forest_guardian",
)

hydra = Character(
    name="Hydra",
    hp=100, damage=16, defense=4, magic=18,
    element="Water", weakness="Electric",
    is_boss=True,
    sprite_key="tide_crawler",
)

thunder_beast = Character(
    name="Thunder Beast",
    hp=120, damage=20, defense=5, magic=25,
    element="Electric", weakness="Grass",
    is_boss=True,
    sprite_key="storm_raven",
)

storm_eagle = Character(
    name="Storm Eagle",
    hp=130, damage=22, defense=6, magic=30,
    element="Air", weakness="Electric",
    is_boss=True,
    sprite_key="storm_eagle",
)

magma_titan = Character(
    name="Magma Titan",
    hp=160, damage=28, defense=8, magic=22,
    element="Fire", weakness="Water",
    is_boss=True,
    sprite_key="magma_titan",
)

shadow_lord = Character(
    name="Shadow Lord",
    hp=140, damage=24, defense=7, magic=35,
    element="Dark", weakness="Electric",
    is_boss=True,
    sprite_key="void_emperor",
)



def reset_boss(boss: Character) -> Character:
    boss.hp = float(boss.max_hp)
    return boss


ROOM_BOSS = {
    "SALA_BATALHA_AGUA":     hydra,
    "SALA_BATALHA_ELETRICA": thunder_beast,
    "SALA_BATALHA_VENTO":    storm_eagle,
    "SALA_BATALHA_FOGO":     magma_titan,
    "SALA_BATALHA_SOMBRA":   shadow_lord,
}