"""Log peristiwa — menambah entri log dengan timestamp game.

Tipe log: narration, npc, player, system (Tianyuan Ling), battle.
"""

from __future__ import annotations

from .state import GameState

LOG_TYPES = {"narration", "npc", "player", "system", "battle"}


def add_log(state: GameState, type_: str, text: str) -> None:
    if type_ not in LOG_TYPES:
        type_ = "narration"
    state.log.append({"type": type_, "text": text, "day": state.day, "hour": state.hour})


def log_delta(state: GameState, start_index: int) -> list[dict]:
    """Entri log baru sejak indeks tertentu (untuk UI/CLI)."""
    return state.log[start_index:]
