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
        sprite_key=None,
    ):
        self.name         = name
        self.max_hp       = hp
        self.hp           = hp
        self.damage       = damage
        self.defense      = defense
        self.element      = element
        self.weakness     = weakness
        self.level        = 1
        self.xp           = 0
        self.is_boss      = is_boss
        self.sprite_key   = sprite_key
        self.is_defending = False   # True enquanto escudo ativo (DefendAction)

        # Callback opcional chamado ao subir de nível.
        # Assinatura: on_level_up(character)
        self.on_level_up = None

    def is_alive(self):
        return self.hp > 0

    def take_damage(self, amount):
        if self.is_defending:
            amount = amount // 2
            self.is_defending = False
        real_damage = max(amount - self.defense, 0)
        self.hp = max(self.hp - real_damage, 0)
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
        self.level   += 1
        self.max_hp  += HP_LEVEL_INCREMENT
        self.damage  += DAMAGE_LEVEL_INCREMENT
        self.defense += DEFENSE_LEVEL_INCREMENT
        self.hp       = self.max_hp
        if self.on_level_up:
            self.on_level_up(self)


class Player(Character):
    """Personagem controlado pelo jogador."""

    def __init__(self, name, hp, damage, defense, element, weakness,
                 sprite_key=None):
        super().__init__(name, hp, damage, defense, element, weakness,
                         is_boss=False, sprite_key=sprite_key)


class Enemy(Character):
    """Inimigo genérico controlado pela IA."""

    def __init__(self, name, hp, damage, defense, element, weakness,
                 is_boss=False, sprite_key=None):
        super().__init__(name, hp, damage, defense, element, weakness,
                         is_boss=is_boss, sprite_key=sprite_key)


class Boss(Enemy):
    """Boss — inimigo especial que sempre tem is_boss=True."""

    def __init__(self, name, hp, damage, defense, element, weakness,
                 sprite_key=None):
        super().__init__(name, hp, damage, defense, element, weakness,
                         is_boss=True, sprite_key=sprite_key)
