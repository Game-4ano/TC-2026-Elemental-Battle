"""
meu_jogo/core/save_system.py

Persiste o ranking de pontuacoes em JSON na pasta do usuario.
Arquivo salvo em: ~/.elemental_battle/highscore.json

Formato atual:
    {"scores": [{"nome": "ART", "pontos": 1286, "data": "2026-08-26"}, ...]}

O formato antigo ({"highscore": N}) e migrado automaticamente na primeira
leitura, sem perder o recorde ja salvo.
"""

import json
import os
from datetime import date

from meu_jogo.core.config import MAX_HISCORES, MAX_NOME_LEN

_SAVE_DIR  = os.path.join(os.path.expanduser("~"), ".elemental_battle")
_SAVE_FILE = os.path.join(_SAVE_DIR, "highscore.json")

# Usado quando o jogador nao informa um nome (ou pela API antiga sem nome).
_NOME_PADRAO = "---"


class SaveSystem:

    # ─── Leitura ──────────────────────────────────────────────────────────────

    def load_scores(self) -> list[dict]:
        """
        Retorna as entradas do ranking ordenadas por pontos (desc).
        Migra o formato antigo se necessario. Lista vazia se nao houver arquivo.
        """
        dados = self._ler_json()
        if dados is None:
            return []

        # Formato antigo: converte o recorde unico em uma entrada e regrava.
        if "scores" not in dados and "highscore" in dados:
            try:
                antigo = self._entrada(_NOME_PADRAO, int(dados["highscore"]))
            except (TypeError, ValueError):
                return []
            self._gravar([antigo])
            return [antigo]

        scores = dados.get("scores")
        if not isinstance(scores, list):
            return []
        return self._ordenar(scores)

    def load_highscore(self) -> int:
        """Retorna a maior pontuacao salva, ou 0. (Assinatura antiga preservada.)"""
        scores = self.load_scores()
        return scores[0]["pontos"] if scores else 0

    def qualifica(self, pontos: int) -> bool:
        """True se `pontos` entraria no top MAX_HISCORES (decide se pede o nome)."""
        scores = self.load_scores()
        if len(scores) < MAX_HISCORES:
            return True
        # Empate nao desbanca quem ja esta no ranking (ver save_score).
        return pontos > scores[-1]["pontos"]

    # ─── Escrita ──────────────────────────────────────────────────────────────

    def save_score(self, nome: str, pontos: int) -> int:
        """
        Insere a entrada, ordena por pontos (desc), corta em MAX_HISCORES e grava.
        Retorna a posicao no ranking (1-based), ou 0 se nao entrou.
        """
        scores = self.load_scores()          # ja normalizadas e ordenadas
        nova   = self._entrada(nome, pontos)
        scores.append(nova)
        # sort estavel: em caso de empate, a entrada nova fica atras das antigas
        scores.sort(key=lambda e: e["pontos"], reverse=True)
        scores = scores[:MAX_HISCORES]
        self._gravar(scores)

        for posicao, entrada in enumerate(scores, start=1):
            if entrada is nova:
                return posicao
        return 0

    def save_highscore(self, score: int) -> bool:
        """
        Shim de compatibilidade com a API antiga (salva sem nome).
        Retorna True se a pontuacao entrou no ranking.
        """
        return self.save_score(_NOME_PADRAO, score) > 0

    # ─── Helpers internos ─────────────────────────────────────────────────────

    @staticmethod
    def _entrada(nome: str, pontos: int) -> dict:
        """Monta uma entrada normalizada do ranking."""
        nome = (str(nome).strip() or _NOME_PADRAO)[:MAX_NOME_LEN]
        return {
            "nome":   nome,
            "pontos": int(pontos),
            "data":   date.today().isoformat(),
        }

    @staticmethod
    def _ordenar(scores: list) -> list[dict]:
        """Descarta entradas malformadas, normaliza e ordena por pontos (desc)."""
        validas = []
        for e in scores:
            if not isinstance(e, dict):
                continue
            try:
                validas.append({
                    "nome":   str(e.get("nome", _NOME_PADRAO))[:MAX_NOME_LEN],
                    "pontos": int(e["pontos"]),
                    "data":   str(e.get("data", "")),
                })
            except (KeyError, TypeError, ValueError):
                continue
        validas.sort(key=lambda e: e["pontos"], reverse=True)
        return validas

    @staticmethod
    def _ler_json():
        """Le o arquivo bruto. None se nao existir ou estiver corrompido."""
        try:
            with open(_SAVE_FILE, "r", encoding="utf-8") as f:
                dados = json.load(f)
            return dados if isinstance(dados, dict) else None
        except (FileNotFoundError, json.JSONDecodeError, ValueError, OSError):
            return None

    @staticmethod
    def _gravar(scores: list[dict]):
        """Grava o ranking, criando a pasta se preciso."""
        try:
            os.makedirs(_SAVE_DIR, exist_ok=True)
            with open(_SAVE_FILE, "w", encoding="utf-8") as f:
                json.dump({"scores": scores}, f, ensure_ascii=False, indent=2)
        except OSError:
            pass   # sem permissao de escrita: o jogo segue sem salvar
