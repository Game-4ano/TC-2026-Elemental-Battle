"""
meu_jogo/core/save_system.py

Persiste o recorde de pontuacao em JSON na pasta do usuario.
Arquivo salvo em: ~/.elemental_battle/highscore.json
"""

import json
import os

_SAVE_DIR  = os.path.join(os.path.expanduser("~"), ".elemental_battle")
_SAVE_FILE = os.path.join(_SAVE_DIR, "highscore.json")


class SaveSystem:

    def save_highscore(self, score: int) -> bool:
        """Salva o score se for maior que o recorde atual. Retorna True se bateu recorde."""
        atual = self.load_highscore()
        if score > atual:
            os.makedirs(_SAVE_DIR, exist_ok=True)
            with open(_SAVE_FILE, "w", encoding="utf-8") as f:
                json.dump({"highscore": score}, f)
            return True
        return False

    def load_highscore(self) -> int:
        """Retorna o recorde salvo, ou 0 se nao houver arquivo."""
        try:
            with open(_SAVE_FILE, "r", encoding="utf-8") as f:
                return int(json.load(f).get("highscore", 0))
        except (FileNotFoundError, json.JSONDecodeError, ValueError):
            return 0
