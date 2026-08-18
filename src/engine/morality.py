"""Skala moralitas (baik → jahat), disimpan sebagai integer.

Digunakan untuk membuka/menutup opsi dialog (kondisi morality_min/max) —
sistem OPSIONAL yang data-driven: tema/cerita boleh memakainya atau tidak.
PENTING: moralitas TIDAK menentukan ending — ending dipilih dari kondisi
`config.arcs[].endings` (lihat session._pick_ending), bukan skala moralitas.
"""

from __future__ import annotations

from ..loader import DataRegistry
from .state import GameState


def clamp_morality(state: GameState, registry: DataRegistry) -> None:
    m = registry.config.get("morality", {})
    lo = m.get("min", -100)
    hi = m.get("max", 100)
    state.player.morality = max(lo, min(hi, state.player.morality))


def adjust(state: GameState, registry: DataRegistry, delta: int) -> None:
    state.player.morality += delta
    clamp_morality(state, registry)
