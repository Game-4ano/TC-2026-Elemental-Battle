from meu_jogo.core.config import (
    XP_PER_LEVEL,
    HP_LEVEL_INCREMENT,
    DAMAGE_LEVEL_INCREMENT,
    DEFENSE_LEVEL_INCREMENT,
)


class Character:
    def __init__(
        self,
        name, hp, damage, defense, element, weakness,
        is_boss=False,
        sprite_key=None,   # chave usada pela sprite_factory (ex: "slime", "hero")
    ):
        self.name       = name
        self.max_hp     = hp
        self.hp         = hp
        self.damage     = damage
        self.defense    = defense
        self.element    = element
        self.weakness   = weakness
        self.level      = 1
        self.xp         = 0
        self.is_boss    = is_boss
        self.sprite_key = sprite_key   # None → fallback retângulo colorido

    def is_alive(self):
        return self.hp > 0

    def take_damage(self, amount):
        real_damage = max(amount - self.defense, 0)
        self.hp -= real_damage
        return real_damage

    def attack(self, target, damage_calculator):
        damage = damage_calculator(self, target)
        return target.take_damage(damage)

    def gain_xp(self, amount):
        self.xp += amount
        while self.xp >= XP_PER_LEVEL:
            self.xp -= XP_PER_LEVEL
            self.level_up()

    def level_up(self):
        self.level += 1
        self.max_hp  += HP_LEVEL_INCREMENT
        self.damage  += DAMAGE_LEVEL_INCREMENT
        self.defense += DEFENSE_LEVEL_INCREMENT
        self.hp       = self.max_hp
        print(f"{self.name} subiu para o nível {self.level}!")