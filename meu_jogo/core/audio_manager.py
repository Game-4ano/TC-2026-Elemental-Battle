"""
meu_jogo/core/audio_manager.py

Gerenciador central de áudio do jogo.
Controla música de fundo e efeitos sonoros (SFX) com carregamento lazy e
tolerância a arquivos ausentes.

Uso:
    manager.audio.play_music("menu_theme")
    manager.audio.play_sfx("hit")
    manager.audio.set_master_volume(0.8)

Pastas de assets:
    meu_jogo/midia/music/   → músicas de fundo (.ogg ou .wav)
    meu_jogo/midia/sfx/     → efeitos sonoros (.ogg ou .wav)
"""

import os
import logging

import pygame

logger = logging.getLogger(__name__)

# Extensões buscadas em ordem de preferência
_EXTS = (".ogg", ".wav", ".mp3")

# Pastas relativas ao pacote meu_jogo/
_PKG_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_MUSIC_DIR = os.path.join(_PKG_DIR, "midia", "music")
_SFX_DIR   = os.path.join(_PKG_DIR, "midia", "sfx")


def _find_file(directory: str, name: str) -> str | None:
    """Retorna o caminho completo do arquivo de áudio ou None se não encontrado."""
    for ext in _EXTS:
        path = os.path.join(directory, name + ext)
        if os.path.isfile(path):
            return path
    return None


class AudioManager:
    """
    Gerenciador de áudio instanciado uma vez no GameManager.

    Carregamento lazy: arquivos SFX só são abertos na primeira reprodução,
    depois ficam cacheados. Músicas são carregadas pelo mixer do pygame.
    Tolerante a arquivos ausentes — registra aviso no log sem travar o jogo.
    """

    def __init__(self):
        self._mixer_ok = False
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            self._mixer_ok = True
        except pygame.error as exc:
            logger.warning("AudioManager: mixer não inicializado: %s", exc)

        self._sfx_cache: dict[str, pygame.mixer.Sound] = {}
        self._current_music: str | None = None

        # Volumes independentes (0.0 – 1.0)
        self._master_vol = 1.0
        self._music_vol  = 0.5
        self._sfx_vol    = 0.8

    # ─── Música ───────────────────────────────────────────────────────────────

    def play_music(self, nome: str, loop: bool = True, volume: float = 0.5):
        """
        Toca uma faixa de música de fundo em loop.
        Não faz nada se a mesma música já estiver tocando.
        """
        if not self._mixer_ok:
            return
        if self._current_music == nome:
            return

        path = _find_file(_MUSIC_DIR, nome)
        if path is None:
            logger.warning(
                "AudioManager: música '%s' não encontrada em %s", nome, _MUSIC_DIR)
            return

        self._music_vol = volume
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(self._music_vol * self._master_vol)
            pygame.mixer.music.play(-1 if loop else 0)
            self._current_music = nome
        except pygame.error as exc:
            logger.warning(
                "AudioManager: erro ao tocar música '%s': %s", nome, exc)

    def stop_music(self, fade_ms: int = 500):
        """Para a música com fade-out opcional."""
        if not self._mixer_ok:
            return
        if fade_ms > 0:
            pygame.mixer.music.fadeout(fade_ms)
        else:
            pygame.mixer.music.stop()
        self._current_music = None

    # ─── SFX ──────────────────────────────────────────────────────────────────

    def play_sfx(self, nome: str, volume: float = 0.8):
        """
        Toca um efeito sonoro. Múltiplos SFX podem soar simultaneamente.
        O arquivo é carregado na primeira chamada e cacheado.
        """
        if not self._mixer_ok:
            return

        if nome not in self._sfx_cache:
            path = _find_file(_SFX_DIR, nome)
            if path is None:
                logger.warning(
                    "AudioManager: SFX '%s' não encontrado em %s", nome, _SFX_DIR)
                return
            try:
                self._sfx_cache[nome] = pygame.mixer.Sound(path)
            except pygame.error as exc:
                logger.warning(
                    "AudioManager: erro ao carregar SFX '%s': %s", nome, exc)
                return

        sound = self._sfx_cache[nome]
        sound.set_volume(volume * self._sfx_vol * self._master_vol)
        sound.play()

    # ─── Volume ───────────────────────────────────────────────────────────────

    def set_master_volume(self, vol: float):
        """Volume geral (0.0–1.0). Afeta música e SFX imediatamente."""
        self._master_vol = max(0.0, min(1.0, vol))
        if self._mixer_ok:
            pygame.mixer.music.set_volume(self._music_vol * self._master_vol)

    def set_music_volume(self, vol: float):
        """Volume exclusivo da música de fundo (0.0–1.0)."""
        self._music_vol = max(0.0, min(1.0, vol))
        if self._mixer_ok:
            pygame.mixer.music.set_volume(self._music_vol * self._master_vol)

    def set_sfx_volume(self, vol: float):
        """Volume exclusivo dos efeitos sonoros (0.0–1.0)."""
        self._sfx_vol = max(0.0, min(1.0, vol))
