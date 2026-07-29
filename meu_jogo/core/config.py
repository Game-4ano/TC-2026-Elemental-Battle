"""
Constantes globais do jogo.
"""

# Configuração da janela
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
FPS = 144
TITLE = "Elemental Battle"

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (70, 170, 70)
DARK_GREEN = (40, 110, 40)
RED = (200, 60, 60)
BLUE = (70, 120, 220)
YELLOW = (220, 200, 70)
BROWN = (120, 80, 40)
GRAY = (180, 180, 180)

# Progressão
XP_PER_LEVEL = 100

HP_LEVEL_INCREMENT = 25
DAMAGE_LEVEL_INCREMENT = 4
DEFENSE_LEVEL_INCREMENT = 2

EXTRA_USES_EVERY = 2
MAX_EXTRA_USES   = 2

DEFAULT_XP_REWARD = 50
BOSS_XP_REWARD = 120
TILE_SIZE = 32

# Escalonamento dos bosses por ordem de enfrentamento (core.progression).
# stat = round(base * (1 + BOSS_GROWTH[stat] * (nivel_de_enfrentamento - 1)))
# Ajustado na Fase 4 (balance_report.py) para: estagio 1 vencivel so no ataque
# basico (>=50% HP final), estagios intermediarios exigem tatica (25-50%),
# e o ultimo estagio pune quem so ataca (HP final negativo sem Curar/Defender).
BOSS_GROWTH = {"hp": 0.60, "damage": 0.38, "defense": 0.20}

# Tempo maximo (s) que a batalha espera pela animacao de morte antes de
# forcar a transicao (Vitoria/GameOver). Rede de seguranca contra travamento.
BATTLE_END_TIMEOUT = 2.0