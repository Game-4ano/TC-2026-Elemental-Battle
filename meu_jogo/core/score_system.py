"""
meu_jogo/core/score_system.py

Sistema de pontuação do jogo Elemental Battle.
Rastreia pontos por batalha e acumulado, combo, bônus e penalidades.

Uso típico:
    manager.score.iniciar_batalha()
    manager.score.increment_combo()
    manager.score.registrar_elemental()
    summary = manager.score.finalizar_batalha(enemy, player.hp, player.max_hp)
"""

import time
import logging

logger = logging.getLogger(__name__)


class ScoreSystem:
    # Pontos base
    PONTOS_INIMIGO = 100
    PONTOS_BOSS    = 500
    BONUS_ELEMENTAL = 50
    BONUS_COMBO_BASE = 25    # multiplicado pelo nível de combo (+25, +50, +75…)
    PENALIDADE_CRITICO = 20  # subtraído (valor positivo, aplicado como negativo)

    # Limiar de golpe crítico: dano > X% do HP máx do defensor
    CRITICO_LIMIAR = 0.15

    # Limite de tempo para bônus de velocidade (segundos)
    TEMPO_RAPIDO_S = 30.0
    MULT_TEMPO     = 1.5

    def __init__(self):
        self._total_score = 0
        self._last_summary: dict = {}
        self._resetar_batalha()

    # ─── Estado interno por batalha ───────────────────────────────────────────

    def _resetar_batalha(self):
        self._battle_score      = 0
        self._combo             = 0
        self._max_combo         = 0
        self._elemental_count   = 0
        self._penalty_total     = 0
        self._combo_bonus_total = 0
        self._base_inimigo      = 0
        self._start_time: float | None = None
        self._log: list[str]    = []

    # ─── API pública ──────────────────────────────────────────────────────────

    def resetar(self):
        """Zera a pontuação acumulada — chamado ao iniciar uma partida nova."""
        self._total_score  = 0
        self._last_summary = {}
        self._resetar_batalha()

    def iniciar_batalha(self):
        """Chama ao entrar em uma batalha nova."""
        self._resetar_batalha()
        self._start_time = time.monotonic()

    def add_points(self, valor: int, motivo: str = ""):
        """Adiciona pontos à batalha atual com log interno para debug."""
        self._battle_score += valor
        sinal = f"+{valor}" if valor >= 0 else str(valor)
        entrada = f"{sinal}  ({motivo})" if motivo else sinal
        self._log.append(entrada)
        logger.debug("ScoreSystem: %s", entrada)

    def increment_combo(self) -> int:
        """
        Registra acerto consecutivo sem tomar dano.
        Retorna o nível de combo atual.
        """
        self._combo += 1
        if self._combo > self._max_combo:
            self._max_combo = self._combo
        bonus = self._combo * self.BONUS_COMBO_BASE
        self._combo_bonus_total += bonus
        self.add_points(bonus, f"combo x{self._combo}")
        return self._combo

    def reset_combo(self):
        """Reseta o combo (chamado ao tomar dano)."""
        self._combo = 0

    def registrar_elemental(self):
        """Registra uso de vantagem elemental (+50 por uso)."""
        self._elemental_count += 1
        self.add_points(self.BONUS_ELEMENTAL, "vantagem elemental")

    def registrar_dano_recebido(self, dano: int, max_hp: int):
        """
        Chamado quando o jogador toma dano.
        Se o dano for crítico (> 15% do HP máx), aplica penalidade e reseta combo.
        Caso contrário, apenas reseta o combo.
        """
        self.reset_combo()
        if dano > max_hp * self.CRITICO_LIMIAR:
            self._penalty_total += self.PENALIDADE_CRITICO
            self.add_points(-self.PENALIDADE_CRITICO, "golpe critico recebido")

    def finalizar_batalha(self, enemy, player_hp: int, player_max_hp: int) -> dict:
        """
        Calcula bônus finais (tempo e HP restante), fecha a pontuação da batalha
        e retorna o breakdown completo para exibição.
        Deve ser chamado apenas em vitória do jogador.
        """
        # Pontos base pelo inimigo derrotado
        base = self.PONTOS_BOSS if enemy.is_boss else self.PONTOS_INIMIGO
        self._base_inimigo = base
        self.add_points(base, "boss derrotado" if enemy.is_boss else "inimigo derrotado")

        # Multiplicador de tempo
        tempo_s   = 0.0
        mult_tempo = 1.0
        if self._start_time is not None:
            tempo_s = time.monotonic() - self._start_time
            if tempo_s < self.TEMPO_RAPIDO_S:
                mult_tempo = self.MULT_TEMPO

        # Multiplicador de HP: 1.0 (0 HP) a 1.5 (HP cheio)
        hp_ratio  = max(player_hp, 0) / max(player_max_hp, 1)
        mult_hp   = 1.0 + hp_ratio * 0.5

        # Aplica multiplicadores ao score bruto
        score_bruto = self._battle_score
        score_final = int(score_bruto * mult_tempo * mult_hp)
        self._battle_score  = score_final
        self._total_score  += score_final

        summary = {
            "score_batalha":    score_final,
            "total":            self._total_score,
            "base_inimigo":     self._base_inimigo,
            "bonus_elemental":  self._elemental_count * self.BONUS_ELEMENTAL,
            "bonus_combo":      self._combo_bonus_total,
            "penalidades":      self._penalty_total,
            "max_combo":        self._max_combo,
            "tempo_s":          round(tempo_s, 1),
            "mult_tempo":       round(mult_tempo, 2),
            "mult_hp":          round(mult_hp, 2),
            "hp_final":         f"{player_hp}/{player_max_hp}",
        }
        self._last_summary = summary
        logger.debug("ScoreSystem: batalha finalizada %s", summary)
        return summary

    # ─── Leitura de estado ────────────────────────────────────────────────────

    def get_battle_score(self) -> int:
        return self._battle_score

    def get_total_score(self) -> int:
        return self._total_score

    def get_combo(self) -> int:
        return self._combo

    def get_max_combo(self) -> int:
        return self._max_combo

    def get_last_battle_summary(self) -> dict:
        return dict(self._last_summary)
