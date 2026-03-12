<<<<<<< HEAD:elemental_battle/core/actions.py
=======
from meu_jogo.core.elements import calculate_damage


>>>>>>> origin/dev:meu_jogo/entidades/acoes.py
class Action:
    """Classe base abstrata para todas as ações de batalha."""
    def __init__(self, name, power, element=None):
        self.name = name
        self.power = power
        self.element = element # Ex: "Fire", "Water", "Grass", "Normal"

    def execute(self, actor, target):
        raise NotImplementedError("As subclasses devem implementar este método.")


class AttackAction(Action):
    """Ação de ataque físico ou mágico que calcula dano e vantagens elementais."""
    
    def get_elemental_multiplier(self, target_element):
        # Lógica clássica estilo Pedra, Papel e Tesoura
        if self.element == "Fire" and target_element == "Grass": return 2.0
        if self.element == "Water" and target_element == "Fire": return 2.0
        if self.element == "Grass" and target_element == "Water": return 2.0
        
        if self.element == "Fire" and target_element == "Water": return 0.5
        # ... adicionar outras fraquezas/resistências ...
        
        return 1.0 # Dano neutro

    def execute(self, actor, target):
        log = [f"{actor.name} usou {self.name}!"]
        
        # Calcula multiplicador elemental
        multiplier = self.get_elemental_multiplier(getattr(target, 'element', 'Normal'))
        
        # Fórmula de dano simples (Pode incluir atributos de Attack e Defense depois)
        dano_final = int(self.power * multiplier)
        target.hp -= dano_final
        
        # Adiciona feedback de efetividade no log
        if multiplier > 1.0:
            log.append("Foi super efetivo!")
        elif multiplier < 1.0:
            log.append("Não foi muito efetivo...")
            
        log.append(f"Causou {dano_final} de dano.")
        
        return log