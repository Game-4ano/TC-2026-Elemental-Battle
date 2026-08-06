"""
Constantes globais do jogo.
"""

# Configuração da janela
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 500
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

HP_LEVEL_INCREMENT = 15
DAMAGE_LEVEL_INCREMENT = 5
DEFENSE_LEVEL_INCREMENT = 3

DEFAULT_XP_REWARD = 50
BOSS_XP_REWARD = 120
TILE_SIZE = 32

# Escalonamento de bosses — progride pela ORDEM de enfrentamento (quantos
# bosses ja foram derrotados na partida), nao pelo elemento/portal escolhido.
# Tier 0 = primeiro boss enfrentado, sempre o mais fraco.
# Valores calibrados por simulacao (meu_jogo/testes/balance_report.py) para
# que cada luta seja arriscada mesmo com o heroi full HP e no nivel esperado
# — o heroi crescia mais rapido que o boss original (+5 dano/+3 defesa por
# nivel vs +3/+1 por tier), entao o jogo so ficava mais facil com o tempo.
BOSS_BASE_HP      = 110
BOSS_BASE_DAMAGE  = 18
BOSS_BASE_DEFENSE = 5

BOSS_HP_PER_TIER      = 16
BOSS_DAMAGE_PER_TIER  = 4
BOSS_DEFENSE_PER_TIER = 2
