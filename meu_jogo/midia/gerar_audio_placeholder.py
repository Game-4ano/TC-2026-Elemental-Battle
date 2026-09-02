"""
meu_jogo/midia/gerar_audio_placeholder.py

Gerador de arquivos de áudio placeholder usando apenas a stdlib do Python
(módulos `wave`, `math`, `struct`, `random`). Nenhuma dependência externa.

Execute UMA VEZ a partir da raiz do projeto:
    python meu_jogo/midia/gerar_audio_placeholder.py

Saída:
    meu_jogo/midia/sfx/    → efeitos sonoros (.wav)
    meu_jogo/midia/music/  → músicas de fundo (.wav)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
COMO SUBSTITUIR PELOS ASSETS FINAIS:
  1. Coloque seus arquivos .ogg (recomendado) ou .wav nas pastas acima,
     usando o mesmo nome sem extensão (ex: "hit.ogg", "battle_theme.ogg").
  2. O AudioManager procura .ogg antes de .wav automaticamente.
  3. Apague os .wav gerados aqui se quiser — o jogo usará o .ogg.
  4. Nenhuma mudança de código é necessária.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import os
import wave
import math
import struct
import random

SAMPLE_RATE  = 44100
CHANNELS     = 1
SAMPLE_WIDTH = 2   # bytes (PCM 16-bit)

_BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MUSIC_DIR = os.path.join(_BASE_DIR, "music")
SFX_DIR   = os.path.join(_BASE_DIR, "sfx")


# ─── Utilitários de baixo nível ──────────────────────────────────────────────

def _clamp16(v: float) -> int:
    return max(-32767, min(32767, int(v * 32767)))

def _write_wav(path: str, samples: list[float]):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    data = struct.pack(f"<{len(samples)}h", *(_clamp16(s) for s in samples))
    with wave.open(path, "w") as f:
        f.setnchannels(CHANNELS)
        f.setsampwidth(SAMPLE_WIDTH)
        f.setframerate(SAMPLE_RATE)
        f.writeframes(data)


# ─── Formas de onda primitivas ───────────────────────────────────────────────

def sine(freq: float, dur: float, amp: float = 0.6) -> list[float]:
    n = int(SAMPLE_RATE * dur)
    return [amp * math.sin(2 * math.pi * freq * i / SAMPLE_RATE) for i in range(n)]

def square(freq: float, dur: float, amp: float = 0.4) -> list[float]:
    n = int(SAMPLE_RATE * dur)
    return [amp * (1.0 if math.sin(2 * math.pi * freq * i / SAMPLE_RATE) >= 0 else -1.0)
            for i in range(n)]

def triangle(freq: float, dur: float, amp: float = 0.5) -> list[float]:
    n = int(SAMPLE_RATE * dur)
    p = SAMPLE_RATE / freq
    return [amp * (2 * abs(2 * (i / p - math.floor(i / p + 0.5))) - 1) for i in range(n)]

def sawtooth(freq: float, dur: float, amp: float = 0.4) -> list[float]:
    n = int(SAMPLE_RATE * dur)
    p = SAMPLE_RATE / freq
    return [amp * 2 * (i / p - math.floor(0.5 + i / p)) for i in range(n)]

def noise(dur: float, amp: float = 0.3) -> list[float]:
    return [amp * (random.random() * 2 - 1) for _ in range(int(SAMPLE_RATE * dur))]

def silence(dur: float) -> list[float]:
    return [0.0] * int(SAMPLE_RATE * dur)


# ─── Operações sobre sinais ──────────────────────────────────────────────────

def mix(*signals: list[float]) -> list[float]:
    """Soma e normaliza múltiplos sinais para evitar clipping."""
    length = max(len(s) for s in signals)
    result = [0.0] * length
    for s in signals:
        for i in range(len(s)):
            result[i] += s[i]
    factor = 1.0 / max(len(signals), 1)
    return [x * factor for x in result]

def concat(*signals: list[float]) -> list[float]:
    out: list[float] = []
    for s in signals:
        out.extend(s)
    return out

def fade(samples: list[float],
         fade_in: float = 0.05, fade_out: float = 0.1) -> list[float]:
    """Aplica rampa linear de entrada e saída para eliminar cliques."""
    result = list(samples)
    n = len(result)
    fi = int(SAMPLE_RATE * fade_in)
    fo = int(SAMPLE_RATE * fade_out)
    for i in range(min(fi, n)):
        result[i] *= i / fi
    for i in range(min(fo, n)):
        result[n - 1 - i] *= i / fo
    return result

def envelope(samples: list[float],
             attack:  float = 0.01,
             decay:   float = 0.10,
             sustain: float = 0.70,
             release: float = 0.10) -> list[float]:
    """Envelope ADSR simples."""
    n = len(samples)
    result = list(samples)
    a = int(SAMPLE_RATE * attack)
    d = int(SAMPLE_RATE * decay)
    r = int(SAMPLE_RATE * release)
    for i in range(n):
        if i < a:
            env = i / max(a, 1)
        elif i < a + d:
            env = 1.0 - (1.0 - sustain) * (i - a) / max(d, 1)
        elif i >= n - r:
            env = sustain * (n - i) / max(r, 1)
        else:
            env = sustain
        result[i] *= env
    return result

def sweep(f0: float, f1: float, dur: float, amp: float = 0.5) -> list[float]:
    """Varredura linear de frequência (chirp) — usado no SFX de portal."""
    n = int(SAMPLE_RATE * dur)
    out = []
    for i in range(n):
        freq = f0 + (f1 - f0) * (i / n)
        out.append(amp * math.sin(2 * math.pi * freq * i / SAMPLE_RATE))
    return out


# ─── Geração de SFX ──────────────────────────────────────────────────────────

def gerar_sfx():
    """Gera todos os efeitos sonoros na pasta sfx/."""

    sfxs = {
        # Fogo: onda quadrada grave (180 Hz) — pesada e incisiva
        "attack_fire": fade(envelope(
            mix(square(180, 0.35), square(90, 0.35, 0.2)),
            attack=0.01, decay=0.05, sustain=0.6, release=0.10,
        )),

        # Água: senoide aguda (880 Hz) com harmônico — suave e líquida
        "attack_water": fade(envelope(
            mix(sine(880, 0.30), sine(1320, 0.30, 0.30)),
            attack=0.02, decay=0.08, sustain=0.5, release=0.12,
        )),

        # Planta: triangular médio (440 Hz) — orgânico e natural
        "attack_grass": fade(envelope(
            mix(triangle(440, 0.30), triangle(660, 0.30, 0.30)),
            attack=0.01, decay=0.06, sustain=0.55, release=0.10,
        )),

        # Elétrico: dente-de-serra + ruído — crepitante e agressivo
        "attack_electric": fade(envelope(
            mix(sawtooth(300, 0.25), noise(0.25, 0.20)),
            attack=0.005, decay=0.03, sustain=0.5, release=0.08,
        )),

        # Sombra: baixa frequência + ruído — sombrio e ameaçador
        "attack_dark": fade(envelope(
            mix(square(80, 0.40, 0.35), noise(0.40, 0.15)),
            attack=0.02, decay=0.10, sustain=0.4, release=0.15,
        )),

        # Vento: varredura ascendente + ruído filtrado — rajada (whoosh)
        "attack_air": fade(envelope(
            mix(sweep(300, 780, 0.30, 0.45), noise(0.30, 0.22)),
            attack=0.04, decay=0.06, sustain=0.55, release=0.12,
        )),

        # Impacto: percussão curta ao acertar o alvo
        "hit": fade(envelope(
            mix(square(120, 0.15, 0.50), noise(0.15, 0.40)),
            attack=0.005, decay=0.05, sustain=0.3, release=0.05,
        )),

        # Super efetivo: dois tons ascendentes rápidos — chamativo
        "super_effective": fade(concat(
            envelope(sine(660, 0.12), attack=0.01, sustain=0.8, release=0.04),
            envelope(sine(880, 0.15), attack=0.01, sustain=0.8, release=0.06),
        )),

        # Seleção de menu: bip limpo e breve
        "menu_select": fade(envelope(
            sine(880, 0.08, 0.50),
            attack=0.005, decay=0.02, sustain=0.7, release=0.03,
        )),

        # Passo: impacto suave e grave ao andar no overworld
        "step": fade(envelope(
            mix(square(80, 0.08, 0.30), noise(0.08, 0.20)),
            attack=0.002, decay=0.03, sustain=0.2, release=0.04,
        )),

        # Portal: varredura ascendente (whoosh) ao entrar no portal
        "portal": fade(sweep(200, 800, 0.50)),

        # Level up: arpejo ascendente (Dó-Mi-Sol-Dó agudo)
        "level_up": fade(concat(
            envelope(sine(523, 0.10), attack=0.01, sustain=0.7, release=0.04),
            envelope(sine(659, 0.10), attack=0.01, sustain=0.7, release=0.04),
            envelope(sine(784, 0.10), attack=0.01, sustain=0.7, release=0.04),
            envelope(sine(1047, 0.20), attack=0.01, sustain=0.8, release=0.08),
        )),

        # Vitória: fanfarra curta ascendente
        "victory": fade(concat(
            envelope(mix(sine(523, 0.15), sine(659, 0.15)),
                     attack=0.01, sustain=0.7, release=0.05),
            envelope(mix(sine(659, 0.15), sine(784, 0.15)),
                     attack=0.01, sustain=0.7, release=0.05),
            envelope(mix(sine(784, 0.30), sine(1047, 0.30)),
                     attack=0.01, sustain=0.8, release=0.10),
        )),

        # Derrota: tons descendentes sombrios
        "defeat": fade(concat(
            envelope(sine(392, 0.20), attack=0.02, sustain=0.6, release=0.08),
            envelope(sine(330, 0.20), attack=0.02, sustain=0.6, release=0.08),
            envelope(sine(262, 0.40), attack=0.02, sustain=0.5, release=0.15),
        )),
    }

    for nome, samples in sfxs.items():
        path = os.path.join(SFX_DIR, nome + ".wav")
        _write_wav(path, samples)
        print(f"  [ok] sfx/{nome}.wav")


# ─── Geração de músicas ──────────────────────────────────────────────────────

def _frase(notas: list[tuple[float, float]], instrumento="sine") -> list[float]:
    """
    Converte lista de (frequência, duração) em amostras de áudio.
    frequência=0 → silêncio.
    """
    out: list[float] = []
    funcs = {"sine": sine, "triangle": triangle, "sawtooth": sawtooth}
    fn = funcs.get(instrumento, sine)
    for freq, dur in notas:
        if freq == 0:
            out.extend(silence(dur))
        else:
            base = mix(fn(freq, dur, 0.5), triangle(freq * 0.5, dur, 0.25))
            out.extend(fade(envelope(base, attack=0.02, decay=0.05,
                                     sustain=0.6, release=0.08),
                            fade_in=0.02, fade_out=0.02))
    return out


def gerar_musicas():
    """Gera os três temas musicais (menu, overworld, batalha)."""

    # ── Tema de menu: tranquilo, dó maior ─────────────────────────────────────
    menu_notas = [
        (523, 0.30), (659, 0.30), (784, 0.30), (880, 0.30),  # C E G A
        (784, 0.30), (659, 0.30), (523, 0.60),
        (0,   0.25),
        (440, 0.30), (523, 0.30), (659, 0.30), (784, 0.30),  # A C E G
        (659, 0.30), (523, 0.60),
        (0,   0.50),
    ]
    loop = _frase(menu_notas) * 3
    _write_wav(os.path.join(MUSIC_DIR, "menu_theme.wav"),
               fade(loop, fade_in=0.8, fade_out=1.5))
    print("  [ok] music/menu_theme.wav")

    # ── Tema de overworld: aventureiro e rítmico ───────────────────────────────
    over_notas = [
        (392, 0.20), (523, 0.20), (659, 0.20), (523, 0.20),  # G C E C
        (392, 0.20), (349, 0.40),
        (0,   0.15),
        (440, 0.20), (523, 0.20), (659, 0.20), (784, 0.20),  # A C E G
        (659, 0.40), (0,   0.20),
        (523, 0.20), (659, 0.20), (784, 0.20), (880, 0.40),  # C E G A
        (784, 0.20), (659, 0.20), (523, 0.40),
        (0,   0.30),
    ]
    loop = _frase(over_notas) * 3
    _write_wav(os.path.join(MUSIC_DIR, "overworld_theme.wav"),
               fade(loop, fade_in=0.5, fade_out=1.5))
    print("  [ok] music/overworld_theme.wav")

    # ── Tema de batalha: intenso, com sawtooth ────────────────────────────────
    battle_notas = [
        (220, 0.15), (0, 0.05), (220, 0.15), (0, 0.05),  # A A staccato
        (261, 0.20), (0, 0.10),
        (246, 0.15), (0, 0.05), (246, 0.15), (0, 0.05),  # B B
        (220, 0.30), (0, 0.15),
        (196, 0.15), (0, 0.05), (220, 0.15), (0, 0.05),
        (261, 0.15), (0, 0.05), (294, 0.30), (0, 0.20),
    ]
    frase_battle: list[float] = []
    for freq, dur in battle_notas:
        if freq == 0:
            frase_battle.extend(silence(dur))
        else:
            s = envelope(
                mix(sawtooth(freq, dur, 0.35), square(freq * 2, dur, 0.20)),
                attack=0.01, decay=0.04, sustain=0.55, release=0.08,
            )
            frase_battle.extend(fade(s, 0.01, 0.02))
    loop = frase_battle * 4
    _write_wav(os.path.join(MUSIC_DIR, "battle_theme.wav"),
               fade(loop, fade_in=0.30, fade_out=1.50))
    print("  [ok] music/battle_theme.wav")


# ─── Ponto de entrada ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("Gerando audios placeholder...")
    print("\n[SFX]")
    gerar_sfx()
    print("\n[Musicas]")
    gerar_musicas()
    print(f"\nConcluido!")
    print(f"  SFX   -> {SFX_DIR}")
    print(f"  Music -> {MUSIC_DIR}")
    print("\nPara substituir pelos assets finais:")
    print("  1. Coloque seus .ogg com o mesmo nome nas pastas acima")
    print("  2. O AudioManager preferira .ogg automaticamente")
    print("  3. Nenhuma mudanca de codigo necessaria")
