"""
meu_jogo/core/save_system.py

Persiste o ranking de pontuacoes em JSON na pasta do usuario.
Arquivo salvo em: ~/.elemental_battle/highscore.json

Formato atual:
    {"scores": [{"nome": "ART", "pontos": 1286, "data": "2026-08-26"}, ...]}

O formato antigo ({"highscore": N}) e migrado automaticamente na primeira
leitura, sem perder o recorde ja salvo.

O historico de partidas fica em arquivo proprio, na raiz do projeto:
    <raiz do projeto>/historico.json
    {"historico": [{"nome": "ART", "score": 1286, "data": "2026-08-26 21:40"}, ...]}
Gravado de forma atomica (.tmp + os.replace) assim que a partida termina.
"""

import json
import os
from datetime import date, datetime

from meu_jogo.core.config import MAX_HISCORES, MAX_NOME_LEN

_SAVE_DIR  = os.path.join(os.path.expanduser("~"), ".elemental_battle")
_SAVE_FILE = os.path.join(_SAVE_DIR, "highscore.json")

# Raiz do projeto (.../TC-2026-Elemental-Battle), calculada a partir deste
# arquivo: core -> meu_jogo -> raiz. Usar __file__ (e nao o diretorio atual)
# garante o mesmo caminho seja qual for a pasta de onde o jogo e iniciado.
_PROJETO_DIR = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Historico de partidas: arquivo proprio, gravado junto dos arquivos do
# projeto (visivel no VS Code) e nao em pasta temporaria do sistema.
_HIST_FILE = os.path.join(_PROJETO_DIR, "historico.json")
_HIST_TMP  = _HIST_FILE + ".tmp"

# Usado quando o jogador nao informa um nome (ou pela API antiga sem nome).
_NOME_PADRAO = "---"


class SaveSystem:

    def __init__(self):
        # Registro gravado por salvar_partida() nesta sessao, para que o nome
        # digitado depois possa corrigi-lo sem criar uma segunda entrada.
        self._ultima_partida: dict | None = None

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

    # ─── Historico de partidas (arquivo proprio: historico.json) ──────────────

    def salvar_partida(self, nome: str, score: int) -> None:
        """
        Registra a partida no historico e grava no disco IMEDIATAMENTE.
        Se o processo morrer logo depois, o registro ja esta salvo.
        Mantem no maximo MAX_HISCORES registros, ordenados por score (desc).
        """
        registro = {
            "nome":  (str(nome).strip() or _NOME_PADRAO)[:MAX_NOME_LEN],
            "score": int(score),
            "data":  datetime.now().strftime("%Y-%m-%d %H:%M"),
        }
        registros = self.carregar_historico()
        registros.append(registro)
        registros.sort(key=lambda r: r["score"], reverse=True)
        registros = registros[:MAX_HISCORES]

        self._gravar_historico(registros)
        self._ultima_partida = registro

    def carregar_historico(self) -> list[dict]:
        """
        Le historico.json. Arquivo ausente ou corrompido = historico vazio
        (lista vazia), nunca uma excecao vazando para o jogo.
        """
        try:
            with open(_HIST_FILE, "r", encoding="utf-8") as f:
                dados = json.load(f)
        except FileNotFoundError:
            return []                      # ainda nao houve nenhuma partida
        except json.JSONDecodeError:
            print("[SaveSystem] historico.json corrompido: exibindo vazio.")
            return []
        except OSError as erro:
            print(f"[SaveSystem] Falha ao ler o historico: {erro}")
            return []

        registros = dados.get("historico") if isinstance(dados, dict) else None
        if not isinstance(registros, list):
            return []
        return self._normalizar_historico(registros)

    def renomear_ultima_partida(self, nome: str) -> None:
        """
        Corrige o nome do registro gravado por salvar_partida() nesta sessao.
        Usado quando o jogador digita o nome depois do fim da partida: a
        pontuacao ja foi para o disco na hora, aqui so o nome e atualizado.
        """
        alvo = self._ultima_partida
        if alvo is None:
            return
        registros = self.carregar_historico()
        for reg in registros:
            # Score + data (ate o minuto) identificam o registro desta partida.
            if reg["score"] == alvo["score"] and reg["data"] == alvo["data"]:
                reg["nome"]  = (str(nome).strip() or _NOME_PADRAO)[:MAX_NOME_LEN]
                alvo["nome"] = reg["nome"]
                self._gravar_historico(registros)
                return

    # ─── Helpers internos ─────────────────────────────────────────────────────

    @staticmethod
    def _normalizar_historico(registros: list) -> list[dict]:
        """Descarta registros malformados, normaliza e ordena por score (desc)."""
        validos = []
        for r in registros:
            if not isinstance(r, dict):
                continue
            try:
                validos.append({
                    "nome":  str(r.get("nome", _NOME_PADRAO))[:MAX_NOME_LEN],
                    "score": int(r["score"]),
                    "data":  str(r.get("data", "")),
                })
            except (KeyError, TypeError, ValueError):
                continue
        validos.sort(key=lambda r: r["score"], reverse=True)
        return validos

    @staticmethod
    def _gravar_historico(registros: list[dict]) -> None:
        """
        Gravacao atomica: escreve tudo no .tmp, forca os bytes para o disco e
        so entao troca pelo arquivo final com os.replace(). Um crash no meio
        da escrita atinge apenas o .tmp; o historico antigo continua intacto.
        """
        try:
            os.makedirs(os.path.dirname(_HIST_FILE), exist_ok=True)
            with open(_HIST_TMP, "w", encoding="utf-8") as f:
                json.dump({"historico": registros}, f,
                          ensure_ascii=False, indent=2)
                f.flush()
                os.fsync(f.fileno())
            os.replace(_HIST_TMP, _HIST_FILE)
        except OSError as erro:
            # Sem permissao de escrita: avisa no console em vez de silenciar.
            print(f"[SaveSystem] Falha ao gravar o historico: {erro}")

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
