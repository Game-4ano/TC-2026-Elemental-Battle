class Character:
    """Representa um personagem jogável ou inimigo."""

    def __init__(self, name, hp, damage, defense, element, weakness, is_boss=False):
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.damage = damage
        self.defense = defense
        self.element = element
        self.weakness = weakness
        self.level = 1
        self.is_boss = is_boss

    def is_alive(self):
        return self.hp > 0

    def take_damage(self, amount):
        real_damage = max(amount - self.defense, 0)
        self.hp -= real_damage
        return real_damage

    def level_up(self):
        self.level += 1
        self.max_hp += 10
        self.damage += 5
        self.defense += 2
        self.hp = self.max_hp
